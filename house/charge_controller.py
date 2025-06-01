import asyncio
import struct
import time

import paho.mqtt.client as mqtt
from mqtt_config import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="red")


class ChargeController:
    def __init__(self, max_charge_wh: int):
        self.max_charge_wh = max_charge_wh

        # Per la simulazione, mettiamo come valore iniziale della carica un valore alto
        self.charge = 0.75 * self.max_charge_wh

        mqtt_client_name = generate_client_name("pub-charcontr")
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_name,
            clean_session=False,
        )
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect(mqtt_address, mqtt_port, 60)

        self.recv_chargebatteries_event = asyncio.Event()
        self.recv_getfrombatteries_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_getfrombatteries, qos=mqtt_qos)
        mqttc.subscribe(topic_internal_chargebatteries, qos=mqtt_qos)

    def on_message(self, mqttc, obj, msg):
        # internal/getfrombatteries
        if msg.topic == topic_internal_getfrombatteries:
            to_give = struct.unpack("f", msg.payload)[0]
            get_from_grid = self.give_charge(to_give)
            self.mqtt_publish(topic_internal_getfromgrid, get_from_grid)
            self.loop.call_soon_threadsafe(self.recv_getfrombatteries_event.set)
        # internal/chargebatteries
        elif msg.topic == topic_internal_chargebatteries:
            charge_batt = struct.unpack("f", msg.payload)[0]
            feed_into_grid = self.charge_batteries(charge_batt)
            self.mqtt_publish(topic_internal_tofeed, feed_into_grid)
            self.loop.call_soon_threadsafe(self.recv_chargebatteries_event.set)

    def mqtt_publish(self, topic: str, payload: float):
        pack_and_publish(self.mqttc, topic, payload)
        print(f"Pub on '{topic}': {payload}")

    def give_charge(self, to_give: int) -> int:
        """
        Scarica le batterie per fornire l'energia richiesta alla casa, se possibile.

        Restituisce l'energia rimasta da fornire.
        """
        if (self.charge - to_give) < 0:
            diff = to_give - self.charge
            self.charge = 0
            return diff
        else:
            self.charge -= to_give
            return 0

    def charge_batteries(self, to_charge: int) -> int:
        """
        Carica le batterie del valore passato, se possibile.

        Restituisce l'energia in eccesso che non sta nelle batterie.
        """
        if (self.charge + to_charge) > self.max_charge_wh:
            diff = self.max_charge_wh - self.charge
            self.charge = self.max_charge_wh
            return to_charge - diff
        else:
            self.charge += to_charge
            return 0

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        await asyncio.gather(
            self.recv_getfrombatteries_event.wait(),
            self.recv_chargebatteries_event.wait(),
        )

        self.mqtt_publish(topic_charge, self.charge)

        self.recv_getfrombatteries_event.clear()
        self.recv_chargebatteries_event.clear()
