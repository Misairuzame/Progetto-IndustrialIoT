import asyncio
import datetime
import random
import struct
import time

import consumption_functions
import paho.mqtt.client as mqtt
from mqtt_config import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="cyan")


class ElectricPanel:
    def __init__(self, start_time, house_profile):
        self.start_time = start_time
        self.house_profile = house_profile

        self.total_panels = 0
        self.get_from_grid = 0
        self.feed_into_grid = 0

        mqtt_client_name = generate_client_name("pub-elpan")
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_name,
            clean_session=False,
        )
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.mqttc.connect(mqtt_address, mqtt_port, 60)

        self.received_total_panels_event = asyncio.Event()
        self.received_get_from_grid_event = asyncio.Event()
        self.received_feed_into_grid_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_totalpanels, qos=mqtt_qos)
        mqttc.subscribe(topic_internal_tofeed, qos=mqtt_qos)
        mqttc.subscribe(topic_internal_getfromgrid, qos=mqtt_qos)

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

    def mqtt_publish(self, topic: str, payload: float):
        pack_and_publish(self.mqttc, topic, payload)
        print(f"Pub on '{topic}': {payload}")

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        now: datetime.datetime = kwargs.get("current_time")

        consumption_required = consumption_functions.calcola_consumo_intervallo(
            self.start_time, now, self.house_profile
        ) * random.uniform(0.75, 1.25)
        # Con un po' di randomicità nel consumo

        self.mqtt_publish(topic_consumption_required, consumption_required)

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
        self.mqtt_publish(topic_internal_getfrombatteries, get_from_batteries)

        # Aspetto il messaggio di consumo dalla rete, che sarà 0, per sincronizzarmi
        await asyncio.gather(self.received_get_from_grid_event.wait())
        self.mqtt_publish(topic_consumption_grid, self.get_from_grid)

        # Carico le batterie con l'energia rimanente (può essere 0)
        self.mqtt_publish(topic_internal_chargebatteries, charge_to_batteries)

        # Aspetto di sapere quanta corrente verrà immessa in rete
        await asyncio.gather(self.received_feed_into_grid_event.wait())
        self.mqtt_publish(topic_feeding, self.feed_into_grid)

        self.received_total_panels_event.clear()
        self.received_get_from_grid_event.clear()
        self.received_feed_into_grid_event.clear()

        self.start_time = now
