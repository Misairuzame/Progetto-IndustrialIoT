import datetime
import json
import re
import struct
import sys
import time
import uuid

import paho.mqtt.client as mqtt
import random_coordinates
from faker import Faker


def get_full_name():
    fake = Faker("it_IT")
    return fake.name()


topic1_name = "telemetry/panel/#"
topic2_name = "telemetry/chargecontroller/#"
topic3_name = "telemetry/electricpanel/#"

topic_internal1 = "internal/totalpanels"

my_qos = 2


class Subscriber:
    def __init__(self, port=1883):
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
        self.mqttc.loop_start()

    def on_connect(self, mqttc, userdata, flags, rc):
        mqttc.subscribe(topic1_name, qos=my_qos)
        mqttc.subscribe(topic2_name, qos=my_qos)
        mqttc.subscribe(topic3_name, qos=my_qos)

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
            }
        }

        with open("log.ndjson", "a") as logfile:
            json.dump(json_dict_clientinfo, logfile)
            logfile.write("\n")

    def on_message(self, mqttc, userdata, msg):
        this_topic = msg.topic
        unpacked = struct.unpack("f", msg.payload)
        measure = round(unpacked[0], 4)
        # Viene ricevuto un dato grezzo, che viene approssimato in quanto
        # si suppone che i dati inviati siano precisi fino alla terza cifra
        # decimale. Può essere un primo esempio di pre-processing.
        if re.match("telemetry/panel/.+", this_topic):
            panel_id = this_topic.replace("telemetry/panel/", "")
            self.current_panels[panel_id] = measure
        elif re.match("telemetry/chargecontroller/.+", this_topic):
            self.current_batteries["total-charge"] = measure
        elif re.match("telemetry/electricpanel/.+", this_topic):
            key_name = this_topic.replace("telemetry/electricpanel/", "")
            self.current_elmeter[key_name] = measure

    def update(self, *args):
        now: datetime.datetime = args[0]
        json_dict = {}
        with open("log.ndjson", "a") as logfile:
            json_dict["clientid"] = self.client_id
            json_dict["telemetry"] = {}
            json_dict["telemetry"]["panels"] = self.current_panels
            json_dict["telemetry"]["batteries"] = self.current_batteries
            json_dict["telemetry"]["elmeter"] = self.current_elmeter
            json_dict["telemetry"]["timestamp"] = now.timestamp()
            tot_prod = 0
            for key, value in self.current_panels.items():
                tot_prod += value
            json_dict["telemetry"]["panels"]["total"] = round(tot_prod, 4)
            # Round permette di evitare errori di calcolo con i float
            # (spesso si hanno risultati del tipo 1234.5678999999999)
            self.mqttc.publish(topic_internal1, struct.pack("f", tot_prod), qos=my_qos)
            self.current_panels = {}
            self.current_batteries = {}
            self.current_elmeter = {}
            json.dump(json_dict, logfile)
            logfile.write("\n")

            json_write = json.dumps(json_dict)
            print(f"{time.time()}\t{__name__}\t{json_write}")
