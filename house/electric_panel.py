import asyncio
import datetime
import random
import struct
import time
import uuid

import my_functions
import paho.mqtt.client as mqtt
from mqtt_topics import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="cyan")


my_qos = 2


class ElectricPanel:
    def __init__(self, start_time, house_profile, port=1883):
        self.start_time = start_time
        self.house_profile = house_profile

        self.total_panels = 0
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

        self.received_total_panels_event = asyncio.Event()
        self.received_get_from_grid_event = asyncio.Event()
        self.received_feed_into_grid_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_totalpanels, qos=my_qos)
        mqttc.subscribe(topic_internal_tofeed, qos=my_qos)
        mqttc.subscribe(topic_internal_getfromgrid, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        if msg.topic == topic_internal_totalpanels:
            self.total_panels = struct.unpack("f", msg.payload)[0]
            self.loop.call_soon_threadsafe(self.received_total_panels_event.set)
        elif msg.topic == topic_internal_getfromgrid:
            self.get_from_grid = struct.unpack("f", msg.payload)[0]
            self.loop.call_soon_threadsafe(self.received_get_from_grid_event.set)
        elif msg.topic == topic_internal_tofeed:
            self.feed_into_grid = struct.unpack("f", msg.payload)[0]
            self.loop.call_soon_threadsafe(self.received_feed_into_grid_event.set)

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        now: datetime.datetime = kwargs.get("current_time")

        consumption_required = my_functions.calcola_consumo_intervallo(
            self.start_time, now, self.house_profile
        ) * random.uniform(0.75, 1.25)
        # Con un po' di randomicità nel consumo

        pkd_consumption_req = struct.pack("f", consumption_required)
        _ = self.mqttc.publish(
            topic_consumption_required, pkd_consumption_req, qos=my_qos
        )
        print(f"Pub on '{topic_consumption_required}': {consumption_required}")

        # Aspetto di ricevere la produzione di tutti i pannelli.
        # A quel punto posso usare l'energia prodotta dai pannelli per il consumo della casa
        await asyncio.gather(self.received_total_panels_event.wait())
        remaining_consumption = consumption_required - self.total_panels

        # Se l'energia è sufficiente a coprire il consumo della casa in questo momento,
        # allora ne chiedo 0 alle batterie e l'energia restante viene inserita nelle
        # batterie, se possibile - in alternativa viene immessa in rete.
        # Altrimenti, chiedo alle batterie di coprire il consumo richiesto, e quindi
        # le caricherò di 0
        get_from_batteries = max(remaining_consumption, 0)
        charge_to_batteries = max(-remaining_consumption, 0)

        # Chiedo energia alle batterie (può essere 0)
        _ = self.mqttc.publish(
            topic_internal_getfrombatteries,
            struct.pack("f", get_from_batteries),
            qos=my_qos,
        )
        print(f"Pub on '{topic_internal_getfrombatteries}': {get_from_batteries}")

        # Aspetto il messaggio di consumo dalla rete, che sarà 0, per sincronizzarmi
        await asyncio.gather(self.received_get_from_grid_event.wait())
        pkd_consumption = struct.pack("f", self.get_from_grid)
        _ = self.mqttc.publish(topic_consumption_grid, pkd_consumption, qos=my_qos)
        print(f"Pub on '{topic_consumption_grid}': {self.get_from_grid}")

        # Carico le batterie con l'energia rimanente (può essere 0)
        _ = self.mqttc.publish(
            topic_internal_chargebatteries,
            struct.pack("f", charge_to_batteries),
            qos=my_qos,
        )
        print(f"Pub on '{topic_internal_chargebatteries}': {charge_to_batteries}")

        # Aspetto di sapere quanta corrente verrà immessa in rete
        await asyncio.gather(self.received_feed_into_grid_event.wait())
        pkd_feed = struct.pack("f", self.feed_into_grid)
        _ = self.mqttc.publish(topic_feeding, pkd_feed, qos=my_qos)
        print(f"Pub on '{topic_feeding}': {self.feed_into_grid}")

        self.received_total_panels_event.clear()
        self.received_get_from_grid_event.clear()
        self.received_feed_into_grid_event.clear()

        self.start_time = now
