import json
import os
import re
import time
from datetime import datetime, timedelta

import requests

ELASTIC_ADDRESS = os.getenv("ELASTIC_ADDRESS", "elasticsearch:9200")

price_per_kwh = 0.3  # €/kWh
pay_per_kwh = 0.15  # €/kWh
# Valori medi, abbastanza standard, più al fine della simulazione
# che per avere una stima 100% realistica


def parse_hours_minutes(time_str: str):
    matches = re.findall(
        r"(\d+)\s*(hour|hours|minute|minutes)", time_str, re.IGNORECASE
    )

    hours = 0
    minutes = 0

    for value, unit in matches:
        if "hour" in unit.lower():
            hours += int(value)
        elif "minute" in unit.lower():
            minutes += int(value)

    return timedelta(hours=hours, minutes=minutes)


simulation_start = datetime.strptime(
    os.getenv("SIMULATION_START", "2025-01-01 00:00"),
    "%Y-%m-%d %H:%M",
)
simulation_step = parse_hours_minutes(os.getenv("SIMULATION_STEP", "1 hour"))
simulation_speed = float(os.getenv("SIMULATION_SPEED", 5.0))

bill_days = int(os.getenv("BILL_DAYS", 7))

current = simulation_start

# Il numero di giorni dopo il quale si produce una bolletta è
# configurabile, in modo da non dover aspettare troppo tempo
# per la raccolta (ma anche per l'elaborazione) dei dati.


def n_simulated_days_in_real_seconds(days: int):
    return ((days * 24 * 60 * 60) / simulation_step.seconds) * simulation_speed


def print_and_sleep():
    print("-" * 86)
    print(
        "Creating report in {} seconds ({} simulated days)".format(
            n_simulated_days_in_real_seconds(bill_days), bill_days
        )
    )
    print(
        "Current real time: {}, real time for next report: {}".format(
            datetime.fromtimestamp(int(time.time())),
            datetime.fromtimestamp(
                int(time.time()) + n_simulated_days_in_real_seconds(bill_days)
            ),
        )
    )
    print("-" * 86)
    time.sleep(n_simulated_days_in_real_seconds(bill_days))


while True:
    from_date = current.timestamp()

    # Attesa del passaggio di una settimana simulata
    print_and_sleep()

    current = current + timedelta(days=7)
    print("Current simulated time:", current.strftime("%Y-%m-%d %H:%M:%s"))

    clients = []

    # Ottenere tutti i ClientID
    url = f"http://{ELASTIC_ADDRESS}/clientinfo/_search"
    headers = {"Content-type": "application/json"}
    body = {
        "query": {"bool": {"must": [{"exists": {"field": "clientinfo.clientid"}}]}},
        "size": 10000,
    }

    req_ids = requests.post(url, headers=headers, json=body)

    hits = req_ids.json()["hits"]["hits"]

    for hit in hits:
        this_client = hit["_source"]["clientinfo"]
        clients.append(this_client)

    # Scroll API per ottenere molti dati di telemetria
    # Il parametro scroll indica per quanto tempo Elastic deve mantenere il contesto dello scroll
    url = f"http://{ELASTIC_ADDRESS}/telemetry/_search?scroll=30s"
    headers = {"Content-type": "application/json"}
    body = {
        "query": {
            "bool": {
                "must": [
                    {"exists": {"field": "telemetry"}},
                    {
                        "range": {
                            "telemetry.timestamp": {
                                "gte": from_date,
                                "lte": current.timestamp(),
                            }
                        }
                    },
                ]
            }
        },
        "size": 10000,
    }

    req_scroll_id = requests.post(url, headers=headers, json=body)
    hits = req_scroll_id.json()["hits"]["hits"]
    scroll_id = req_scroll_id.json()["_scroll_id"]

    url = f"http://{ELASTIC_ADDRESS}/_search/scroll"
    headers = {"Content-type": "application/json"}
    body = {"scroll": "30s", "scroll_id": scroll_id}

    req_telemetry = requests.post(url, headers=headers, json=body)
    this_hits = req_telemetry.json()["hits"]["hits"]

    while len(this_hits) > 0:
        hits += this_hits
        req_telemetry = requests.post(url, headers=headers, json=body)
        this_hits = req_telemetry.json()["hits"]["hits"]
        print("hits: {}".format(len(this_hits)))

    clients_with_bill = []

    for client in clients:
        a_client = {}
        a_client["clientinfo"] = client
        a_client["bill-timestamp"] = int(current.timestamp())
        a_client["period"] = "1w"

        total_fed = 0
        total_grid = 0
        total_house = 0
        for hit in hits:
            if hit["_source"]["clientid"] == a_client["clientinfo"]["clientid"]:
                try:
                    hit_elmeter = hit["_source"]["telemetry"]["elmeter"]
                    total_fed += hit_elmeter["feeding"]
                    total_grid += hit_elmeter["consumption-grid"]
                    total_house += hit_elmeter["consumption-required"]
                except:
                    print("Errore nel seguente risultato: {}".format(hit["_source"]))

        a_client["fed-into-grid"] = round(total_fed, 4)
        a_client["consumed-grid"] = round(total_grid, 4)
        a_client["total-house-consumed"] = round(total_house, 4)

        # Diviso 1000: Wh -> kWh
        gained_feeding = round(total_fed * pay_per_kwh / 1000, 2)
        a_client["gained-feeding"] = gained_feeding

        # Diviso 1000: Wh -> kWh
        price_consumed = round(total_grid * price_per_kwh / 1000, 2)
        a_client["price-consumed"] = price_consumed

        total_to_pay = round(price_consumed - gained_feeding, 2)
        if total_to_pay < 0:
            a_client["total-to-pay"] = 0
            a_client["to-be-credited"] = -total_to_pay
        else:
            a_client["total-to-pay"] = total_to_pay
            a_client["to-be-credited"] = 0
        clients_with_bill.append(a_client)

    root_client = {}
    root_client["billing"] = clients_with_bill
    with open("client_bills.json", "w") as billfile:
        json.dump(root_client, billfile, indent=5)

    print(clients_with_bill)

    # Inserimento delle bollette in Elasticsearch
    url = f"http://{ELASTIC_ADDRESS}/elaboration/_doc/"
    for bill in clients_with_bill:
        billurl = "{}{}-{}".format(
            url, bill["clientinfo"]["clientid"], bill["bill-timestamp"]
        )
        headers = {"Content-type": "application/json"}
        req_insert = requests.put(billurl, headers=headers, json=bill)
        print(req_insert.json())
