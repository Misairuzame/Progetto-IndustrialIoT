import asyncio
import random
import struct
import time
import uuid

import paho.mqtt.client as mqtt
from print_color import print as prnt


def print(*args):
    prnt(*args, color="red")


topic_charge = "telemetry/chargecontroller/c1"

topic_internal_totalpanels = "internal/totalpanels"
topic_internal_tofeed = "internal/tofeed"
topic_internal_getfrombatteries = "internal/getfrombatteries"
topic_internal_getfromgrid = "internal/getfromgrid"

my_qos = 2


class ChargeController:
    def __init__(self, port=1883):
        # Unità di misura: Wh. Il sistema di accumulo di ogni casa
        # viene scelto casualmente fra 5 e 12 kWh.
        self.max_charge_wh = random.randint(5, 12) * 1000

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

        self.recv_totalpanels_event = asyncio.Event()
        self.recv_getfrombatteries_event = asyncio.Event()

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal_totalpanels, qos=my_qos)
        mqttc.subscribe(topic_internal_getfrombatteries, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        if msg.topic == topic_internal_totalpanels:
            produced_now = struct.unpack("f", msg.payload)[0]
            feed_into_grid = self.charge_batteries(produced_now)
            mqttc.publish(
                topic_internal_tofeed,
                struct.pack("f", float(feed_into_grid)),
                qos=my_qos,
            )
            print(
                f"{time.time()}\t{__name__}\tPub on '{topic_internal_tofeed}': {feed_into_grid}"
            )
            self.loop.call_soon_threadsafe(self.recv_totalpanels_event.set)
        elif msg.topic == topic_internal_getfrombatteries:
            to_give = struct.unpack("f", msg.payload)[0]
            get_from_grid = self.give_charge(to_give)
            mqttc.publish(
                topic_internal_getfromgrid,
                struct.pack("f", float(get_from_grid)),
                qos=my_qos,
            )
            print(
                f"{time.time()}\t{__name__}\tPub on '{topic_internal_getfromgrid}': {get_from_grid}"
            )
            self.loop.call_soon_threadsafe(self.recv_getfrombatteries_event.set)

    def give_charge(self, to_give: int) -> int:
        """
        Scarica le batterie per fornire l'energia richiesta alla casa, se possibile.

        Se le batterie possono fornire tutta l'energia
        che serve in un certo istante, allora lo fanno,
        decrementando la variabile che traccia quanta carica
        contengono e restituendo la potenza fornita. Se non
        possono fornirla tutta, allora (per semplicità) non
        forniscono alcuna carica.

        Args:
            to_give: Quanta carica prelevare dalle batterie.

        Returns:
            0 se tutta la carica richiesta è stata fornita dalle batterie,
            altrimenti la carica da prelevare dalla rete (per semplicità,
            tutta quella richiesta).
        """
        if (self.charge - to_give) < 0:
            return to_give
        else:
            self.charge -= to_give
            return 0

    def charge_batteries(self, to_charge: int) -> int:
        """
        Carica le batterie del valore passato, se possibile.

        Se le batterie possono contenere tutta l'energia che
        gli viene mandata in un istante, allora si caricano,
        sennò verrà fornita alla rete.

        Args:
            to_charge: Quanta carica inserire nelle batterie.

        Returns:
            0 se tutta la carica è stata inserita nelle batterie,
            altrimenti la carica che non c'è stata (per semplicità,
            tutta quella richiesta).
        """
        if (self.charge + to_charge) > self.max_charge_wh:
            return to_charge
        else:
            self.charge += to_charge
            return 0

    async def update(self, *args):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print(
                f"{time.time()}\t{__name__}\tSkipping the first step to sync all devices..."
            )
            self.started = True
            return

        await asyncio.gather(
            self.recv_getfrombatteries_event.wait(),
            self.recv_totalpanels_event.wait(),
        )

        pkd_charge = struct.pack("f", self.charge)
        _ = self.mqttc.publish(topic_charge, pkd_charge, qos=my_qos)
        print(f"{time.time()}\t{__name__}\tPub on '{topic_charge}': {self.charge}")

        self.recv_getfrombatteries_event.clear()
        self.recv_totalpanels_event.clear()
