import asyncio
import datetime
import random
import struct
import time
import uuid

import my_functions
import paho.mqtt.client as mqtt
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="cyan")


topic_consumption_grid = "telemetry/electricpanel/consumption-grid"
topic_feeding = "telemetry/electricpanel/feeding"
topic_consumption_required = "telemetry/electricpanel/consumption-required"

topic_internal_tofeed = "internal/tofeed"
topic_internal_getfombatteries = "internal/getfrombatteries"
topic_internal_getfromgrid = "internal/getfromgrid"

my_qos = 2


class ElectricPanel:
    def __init__(self, start_time, port=1883):
        self.start_time = start_time
        self.get_from_grid = 0
        self.feed_into_grid = 0

        mqtt_name = "pub-elpan-"
        mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_name)]
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_name + mqtt_rand_id,
        )
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.mqttc.connect("localhost", port, 60)

        self.received_get_from_grid_event = asyncio.Event()
        self.received_feed_into_grid_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_tofeed, qos=my_qos)
        mqttc.subscribe(topic_internal_getfromgrid, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        if msg.topic == topic_internal_getfromgrid:
            self.get_from_grid = struct.unpack("f", msg.payload)[0]
            self.loop.call_soon_threadsafe(self.received_get_from_grid_event.set)
        elif msg.topic == topic_internal_tofeed:
            self.feed_into_grid = struct.unpack("f", msg.payload)[0]
            self.loop.call_soon_threadsafe(self.received_feed_into_grid_event.set)

    async def update(self, *args):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        now: datetime.datetime = args[0]

        consumption_required = my_functions.calcola_consumo_intervallo(
            self.start_time, now
        ) * random.uniform(0.75, 1.25)
        # Con un po' di randomicità nel consumo

        pkd_consumption_req = struct.pack("f", consumption_required)
        _ = self.mqttc.publish(
            topic_consumption_required, pkd_consumption_req, qos=my_qos
        )
        print(f"Pub on '{topic_consumption_required}': {consumption_required}")

        # Simulazione: il quadro elettrico "chiede" energia alle batterie, se è possibile le batterie
        # gliela forniscono tutta, sennò (per semplicità) non gliene forniscono alcuna e tutta la
        # corrente viene presa dalla rete elettrica.
        _ = self.mqttc.publish(
            topic_internal_getfombatteries,
            struct.pack("f", consumption_required),
            qos=my_qos,
        )
        print(f"Pub on '{topic_internal_getfombatteries}': {consumption_required}")

        # Devo aver ricevuto get_from_grid per poter pubblicare
        await asyncio.gather(self.received_get_from_grid_event.wait())
        pkd_consumption = struct.pack("f", self.get_from_grid)
        _ = self.mqttc.publish(topic_consumption_grid, pkd_consumption, qos=my_qos)
        print(f"Pub on '{topic_consumption_grid}': {self.get_from_grid}")

        # Devo aver ricevuto feed_into_grid per poter pubblicare
        await asyncio.gather(self.received_feed_into_grid_event.wait())
        pkd_feed = struct.pack("f", self.feed_into_grid)
        _ = self.mqttc.publish(topic_feeding, pkd_feed, qos=my_qos)
        print(f"Pub on '{topic_feeding}': {self.feed_into_grid}")

        self.received_get_from_grid_event.clear()
        self.received_feed_into_grid_event.clear()

        self.start_time = now
