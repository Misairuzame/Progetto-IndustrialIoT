import requests
import json
import time
import time_scaling

price_per_kwh = 0.3 #€/kWh
pay_per_kwh = 0.15 #€/kWh
# Valori medi, abbastanza standard, più
# al fine della simulazione che per avere
# una stima 100% realistica

from_date = time_scaling.get_one_week_ago_scaled() # Una settimana "simulata" fa
#from_date = time.time()-(86400*2), # 2 giorni "reali" fa

# Al fine della simulazione poniamo una fatturazione settimanale,
# in modo da non dover aspettare troppo tempo per la raccolta
# (ma anche per l'elaborazione) dei dati.

while True:
    sleep_until = time_scaling.get_time_scale()*7
    print("-------------------------------------------")
    print("Creating report in {} seconds".format(sleep_until))
    print("-------------------------------------------")
    time.sleep(sleep_until)
    clients = []

    url = "http://localhost:9200/clientinfo/_search"
    headers = {"Content-type": "application/json"}
    body = {
        "query": {
        "bool": {
        "must": [
            {
                "exists": {
                    "field": "clientinfo.clientid"
                }
            }
        ]
        }
    },
    "size": 10000
    }

    req_ids = requests.post(url, headers=headers, json=body)

    hits = req_ids.json()["hits"]["hits"]

    for hit in hits:
        this_client = hit["_source"]["clientinfo"]
        clients.append(this_client)

    # SCROLL API
    url = "http://localhost:9200/telemetry/_search?scroll=30s"
    headers = {"Content-type": "application/json"}
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "exists": {
                            "field": "telemetry"
                        }
                    },
                    {
                        "range": {
                            "telemetry.timestamp": {
                                "gte": from_date,
                                "lte": time.time()
                            }
                        }
                    }
                ]
            }
    },
    "size": 10000
    }

    req_scroll_id = requests.post(url, headers=headers, json=body)
    hits = req_scroll_id.json()["hits"]["hits"]
    scroll_id = req_scroll_id.json()["_scroll_id"]

    url = "http://localhost:9200/_search/scroll"
    headers = {"Content-type": "application/json"}
    body = {
        "scroll": "30s",
        "scroll_id": scroll_id
    }

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
        a_client["bill-timestamp"] = int(time.time())
        a_client["period"] = "1w"
        total_fed = 0
        total_grid = 0
        total_house = 0
        for hit in hits:
            if hit["_source"]["clientid"] == a_client["clientinfo"]["clientid"]:
                try:
                    total_fed += hit["_source"]["telemetry"]["elmeter"]["feeding"]
                    total_grid += hit["_source"]["telemetry"]["elmeter"]["consumption-grid"]
                    total_house += hit["_source"]["telemetry"]["elmeter"]["consumption-required"]
                except:
                    print("Errore nel seguente risultato: {}".format(hit["_source"]))
        a_client["fed-into-grid"] = round(total_fed, 4)
        a_client["consumed-grid"] = round(total_grid, 4)
        a_client["total-house-consumed"] = round(total_house, 4)
        gained_feeding = round(total_fed * pay_per_kwh, 2)
        a_client["gained-feeding"] = gained_feeding
        price_consumed = round(total_grid * price_per_kwh)
        a_client["price-consumed"] = price_consumed
        total_to_pay = price_consumed - gained_feeding
        if total_to_pay < 0:
            a_client["total-to-pay"] = 0
            a_client["to-be-credited"] = total_to_pay
        elif total_to_pay == 0:
            a_client["total-to-pay"] = 0
            a_client["to-be-credited"] = 0
        else:
            a_client["total-to-pay"] = total_to_pay
            a_client["to-be-credited"] = 0
        clients_with_bill.append(a_client)

    root_client = {}
    root_client["billing"] = clients_with_bill
    with open('client_bills.json', 'w') as billfile:
        json.dump(root_client, billfile, indent=5)


    # Inserimento in Elasticsearch
    url = "http://localhost:9200/elaboration/_doc/"
    for bill in clients_with_bill:
        billurl = "{}{}-{}".format(url, bill["clientinfo"]["clientid"], bill["bill-timestamp"])
        headers = {"Content-type": "application/json"}
        req_insert = requests.put(billurl, headers=headers, json=bill)
        print(req_insert.json())