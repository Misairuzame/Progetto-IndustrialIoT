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


client_id = str(uuid.uuid4())
client_name = get_full_name()
(longitude, latitude) = random_coordinates.random_point_in_country("Italy")

topic1_name = "telemetry/panel/#"
topic2_name = "telemetry/chargecontroller/#"
topic3_name = "telemetry/electricpanel/#"
topic_internal1 = "internal/totalpanels"

current_panels = None
current_batteries = None
current_elmeter = None

json_dict = {}

json_dict_clientinfo = {
    "clientinfo": {
        "clientid": client_id,
        "clientname": client_name,
        "position": {"lat": latitude, "lon": longitude},
    }
}

my_qos = 2


def init_data():
    global current_panels, current_batteries, current_elmeter
    current_panels = {}
    current_batteries = {}
    current_elmeter = {}


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic1_name, qos=my_qos)
    client.subscribe(topic2_name, qos=my_qos)
    client.subscribe(topic3_name, qos=my_qos)

    # Alla connessione vengono registrati nel log i dati dell'utente, che
    # verranno poi inviati a Kafka
    with open("log.ndjson", "a") as logfile:
        json.dump(json_dict_clientinfo, logfile)
        logfile.write("\n")


def on_message(client, userdata, msg):
    global current_panels, current_batteries, current_elmeter
    this_topic = msg.topic
    unpacked = struct.unpack("f", msg.payload)
    measure = round(unpacked[0], 4)
    # Viene ricevuto un dato grezzo, che viene approssimato in quanto
    # si suppone che i dati inviati siano precisi fino alla terza cifra
    # decimale. Può essere un primo esempio di pre-processing.

    if re.match("telemetry/panel/.+", this_topic):
        panel = this_topic.replace("telemetry/panel/", "")
        current_panels[panel] = measure
    elif re.match("telemetry/chargecontroller/.+", this_topic):
        current_batteries["total-charge"] = measure
    elif re.match("telemetry/electricpanel/.+", this_topic):
        key_name = this_topic.replace("telemetry/electricpanel/", "")
        current_elmeter[key_name] = measure


port = 1883
if len(sys.argv) > 1:
    port = int(sys.argv[1])

mqtt_client_name = "sub-contatore-"
mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
mqttc = mqtt.Client(client_id=mqtt_client_name + mqtt_rand_id, clean_session=False)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", port, 60)
init_data()
mqttc.loop_start()


def update(*args):
    now: datetime.datetime = args[0]
    with open("log.ndjson", "a") as logfile:
        json_dict["clientid"] = client_id
        json_dict["telemetry"] = {}
        json_dict["telemetry"]["panels"] = current_panels
        json_dict["telemetry"]["batteries"] = current_batteries
        json_dict["telemetry"]["elmeter"] = current_elmeter
        json_dict["telemetry"]["timestamp"] = now.timestamp()
        tot_prod = 0
        for key, value in current_panels.items():
            tot_prod += value
        json_dict["telemetry"]["panels"]["total"] = round(tot_prod, 4)
        # Round permette di evitare errori di calcolo con i float
        # (spesso si hanno risultati del tipo 1234.5678999999999)
        mqttc.publish(topic_internal1, struct.pack("f", tot_prod), qos=my_qos)
        init_data()
        json.dump(json_dict, logfile)
        logfile.write("\n")

        json_write = json.dumps(json_dict)
        print(f"{time.time()}\t{__name__}\t{json_write}")
