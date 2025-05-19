import asyncio
import struct
import time
import uuid

import paho.mqtt.client as mqtt
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="red")


topic_charge = "telemetry/chargecontroller/c1"

topic_internal_tofeed = "internal/tofeed"
topic_internal_getfrombatteries = "internal/getfrombatteries"
topic_internal_getfromgrid = "internal/getfromgrid"
topic_internal_chargebatteries = "internal/chargebatteries"

my_qos = 2


class ChargeController:
    def __init__(self, max_charge_wh: int, port=1883):
        self.max_charge_wh = max_charge_wh

        # Per la simulazione, mettiamo come valore iniziale della carica un valore alto
        self.charge = 0.75 * self.max_charge_wh

        mqtt_client_name = "pub-charcontr-"
        mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_name + mqtt_rand_id,
        )
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.connect("localhost", port, 60)

        self.recv_chargebatteries_event = asyncio.Event()
        self.recv_getfrombatteries_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_getfrombatteries, qos=my_qos)
        mqttc.subscribe(topic_internal_chargebatteries, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        # internal/getfrombatteries
        if msg.topic == topic_internal_getfrombatteries:
            to_give = struct.unpack("f", msg.payload)[0]
            get_from_grid = self.give_charge(to_give)
            mqttc.publish(
                topic_internal_getfromgrid,
                struct.pack("f", float(get_from_grid)),
                qos=my_qos,
            )
            print(f"Pub on '{topic_internal_getfromgrid}': {get_from_grid}")
            self.loop.call_soon_threadsafe(self.recv_getfrombatteries_event.set)
        # internal/chargebatteries
        elif msg.topic == topic_internal_chargebatteries:
            charge_batt = struct.unpack("f", msg.payload)[0]
            feed_into_grid = self.charge_batteries(charge_batt)
            mqttc.publish(
                topic_internal_tofeed,
                struct.pack("f", float(feed_into_grid)),
                qos=my_qos,
            )
            print(f"Pub on '{topic_internal_tofeed}': {feed_into_grid}")
            self.loop.call_soon_threadsafe(self.recv_chargebatteries_event.set)

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

        pkd_charge = struct.pack("f", self.charge)
        _ = self.mqttc.publish(topic_charge, pkd_charge, qos=my_qos)
        print(f"Pub on '{topic_charge}': {self.charge}")

        self.recv_getfrombatteries_event.clear()
        self.recv_chargebatteries_event.clear()
