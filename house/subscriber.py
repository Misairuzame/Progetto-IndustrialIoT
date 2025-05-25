import asyncio
import datetime
import json
import re
import struct
import time
import uuid

import aiofiles
import paho.mqtt.client as mqtt
import random_coordinates
from faker import Faker
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="purple")


def get_full_name():
    fake = Faker("it_IT")
    return fake.name()


all_topics_panel = "telemetry/panel/#"
topic_chargecontroller = "telemetry/chargecontroller/c1"

topic_elpan_consumption_grid = "telemetry/electricpanel/consumption-grid"
topic_elpan_feeding = "telemetry/electricpanel/feeding"
topic_elpan_consumption_required = "telemetry/electricpanel/consumption-required"

topic_internal_totalpanels = "internal/totalpanels"

my_qos = 2


class Subscriber:
    def __init__(
        self,
        simulation_start: datetime.datetime,
        num_of_panels: int,
        max_tot_prod: int,
        max_charge_wh: int,
        port=1883,
    ):
        self.simulation_start = simulation_start
        self.num_of_panels = num_of_panels
        self.max_tot_prod = max_tot_prod
        self.max_charge_wh = max_charge_wh

        self.current_panels = {}
        self.current_batteries = {}
        self.current_elmeter = {}

        mqtt_client_name = "sub-contatore-"
        mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
        self.mqttc = mqtt.Client(
            client_id=mqtt_client_name + mqtt_rand_id, clean_session=False
        )
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.connect("localhost", port, 60)

        self.recv_totalpanels_event = asyncio.Event()
        self.recv_chargecontroller_event = asyncio.Event()
        self.recv_electricpanel_cons_grid_event = asyncio.Event()
        self.recv_electricpanel_feeding_event = asyncio.Event()
        self.recv_electricpanel_cons_req_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, userdata, flags, rc):
        mqttc.subscribe(all_topics_panel, qos=my_qos)
        mqttc.subscribe(topic_internal_totalpanels, qos=my_qos)
        mqttc.subscribe(topic_chargecontroller, qos=my_qos)

        mqttc.subscribe(topic_elpan_consumption_grid, qos=my_qos)
        mqttc.subscribe(topic_elpan_feeding, qos=my_qos)
        mqttc.subscribe(topic_elpan_consumption_required, qos=my_qos)

        # Alla connessione vengono registrati nel log i dati dell'utente, che
        # verranno poi inviati a Kafka
        self.client_id = str(uuid.uuid4())
        client_name = get_full_name()
        (longitude, latitude) = random_coordinates.random_point_in_country("Italy")

        json_dict_clientinfo = {
            "clientinfo": {
                "clientid": self.client_id,
                "clientname": client_name,
                "position": {"lat": latitude, "lon": longitude},
                "number_of_panels": self.num_of_panels,
                "max_total_production": self.max_tot_prod,
                "max_storage_capacity": self.max_charge_wh,
                "timestamp": self.simulation_start.timestamp(),
            }
        }

        with open("log.ndjson", "a") as logfile:
            json.dump(json_dict_clientinfo, logfile)
            logfile.write("\n")

    def on_message(self, mqttc, userdata, msg):
        this_topic = msg.topic
        unpacked = struct.unpack("f", msg.payload)
        measure = round(unpacked[0], 4)
        # Round permette di evitare errori di calcolo con i float
        # (spesso si hanno risultati del tipo 1234.5678999999999).
        # Viene ricevuto un dato grezzo, che viene approssimato in quanto
        # si suppone che i dati inviati siano precisi fino alla terza cifra
        # decimale. Può essere un primo esempio di pre-processing.

        # telemetry/panel/p{n}
        if re.match("telemetry/panel/.+", this_topic):
            panel_id = this_topic.replace("telemetry/panel/", "")
            self.current_panels[panel_id] = measure
        # internal/totalpanels
        elif this_topic == topic_internal_totalpanels:
            self.total_panels = measure
            self.loop.call_soon_threadsafe(self.recv_totalpanels_event.set)
        # telemetry/chargecontroller/c1
        elif this_topic == topic_chargecontroller:
            self.current_batteries["total-charge"] = measure
            self.loop.call_soon_threadsafe(self.recv_chargecontroller_event.set)
        # telemetry/electricpanel/consumption-grid
        elif this_topic == topic_elpan_consumption_grid:
            key_name = this_topic.replace("telemetry/electricpanel/", "")
            self.current_elmeter[key_name] = measure
            self.loop.call_soon_threadsafe(self.recv_electricpanel_cons_grid_event.set)
        # telemetry/electricpanel/feeding
        elif this_topic == topic_elpan_feeding:
            key_name = this_topic.replace("telemetry/electricpanel/", "")
            self.current_elmeter[key_name] = measure
            self.loop.call_soon_threadsafe(self.recv_electricpanel_feeding_event.set)
        # telemetry/electricpanel/consumption-required
        elif this_topic == topic_elpan_consumption_required:
            key_name = this_topic.replace("telemetry/electricpanel/", "")
            self.current_elmeter[key_name] = measure
            self.loop.call_soon_threadsafe(self.recv_electricpanel_cons_req_event.set)

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        now: datetime.datetime = kwargs.get("current_time")
        json_dict = {}
        # Devo aspettare:
        # - di aver ricevuto tutti i pannelli. Visto che l'inverter attende
        # a sua volta tutti i pannelli e poi pubblica sul topic interno la
        # produzione totale, allora posso aspettare direttamente di aver
        # ricevuto la produzione totale dall'inverter.
        # - di aver ricevuto i dati dal controller di carica.
        # - di aver ricevuto i dati dal quadro elettrico.
        await asyncio.gather(
            self.recv_totalpanels_event.wait(),
            self.recv_chargecontroller_event.wait(),
            self.recv_electricpanel_cons_grid_event.wait(),
            self.recv_electricpanel_feeding_event.wait(),
            self.recv_electricpanel_cons_req_event.wait(),
        )

        async with aiofiles.open("log.ndjson", "a") as logfile:
            json_dict["clientid"] = self.client_id
            json_dict["telemetry"] = {}

            json_dict["telemetry"]["panels"] = self.current_panels
            json_dict["telemetry"]["panels"]["total"] = self.total_panels

            json_dict["telemetry"]["batteries"] = self.current_batteries

            json_dict["telemetry"]["elmeter"] = self.current_elmeter

            json_dict["telemetry"]["timestamp"] = now.timestamp()

            tries = 3
            throw = True
            # try "tries" times, or just continue if everything expected is in json_dict
            while tries > 0 and throw:
                try:
                    _ = json_dict["clientid"]
                    _ = json_dict["telemetry"]
                    _ = json_dict["telemetry"]["panels"]
                    _ = json_dict["telemetry"]["panels"]["total"]
                    _ = json_dict["telemetry"]["batteries"]
                    _ = json_dict["telemetry"]["batteries"]["total-charge"]
                    _ = json_dict["telemetry"]["elmeter"]
                    _ = json_dict["telemetry"]["elmeter"]["consumption-grid"]
                    _ = json_dict["telemetry"]["elmeter"]["feeding"]
                    _ = json_dict["telemetry"]["elmeter"]["consumption-required"]
                    _ = json_dict["telemetry"]["timestamp"]
                    throw = False
                except KeyError as e:
                    print("json_dict key not found:", e)
                    throw = True
                    print(
                        f"Not all fields were present in log ({e} is missing): {json_dict=}, retrying... ({tries=})"
                    )
                    # Time.sleep will block the entire process!
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print("json_dict exception:", e)
                    throw = True
                    print(
                        f"Other exception in json_dict ({e}): {json_dict=}, retrying... ({tries=})"
                    )
                    # Time.sleep will block the entire process!
                    await asyncio.sleep(0.5)
                tries -= 1

            if throw:
                print(
                    f"Not all fields were present in log: {json_dict=}, no retries left!"
                )
                # make container unhealthy
                import shutil

                shutil.move("/app/log.ndjson", "/app/log-copy.ndjson")
                raise AssertionError(
                    f"Not all fields are present in this log! {json_dict=}"
                )

            json_write = json.dumps(json_dict)
            await logfile.write(json_write + "\n")

            print(f"Wrote to log.ndjson: {json_write}")

            self.current_panels = {}
            self.current_batteries = {}
            self.current_elmeter = {}

            self.recv_totalpanels_event.clear()
            self.recv_chargecontroller_event.clear()
            self.recv_electricpanel_cons_grid_event.clear()
            self.recv_electricpanel_feeding_event.clear()
            self.recv_electricpanel_cons_req_event.clear()
