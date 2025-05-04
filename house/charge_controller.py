import random
import struct
import time
import uuid

import paho.mqtt.client as mqtt

topic_internal1 = "internal/totalpanels"
topic_internal2 = "internal/tofeed"
topic_internal3 = "internal/getfrombatteries"
topic_internal4 = "internal/getfromgrid"

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
        self.topic = "telemetry/chargecontroller/c1"
        self.mqttc.loop_start()

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal1, qos=my_qos)
        mqttc.subscribe(topic_internal2, qos=my_qos)
        mqttc.subscribe(topic_internal3, qos=my_qos)
        mqttc.subscribe(topic_internal4, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        if msg.topic == topic_internal1:
            produced_now = struct.unpack("f", msg.payload)[0]
            feed_into_grid = self.charge_batteries(produced_now)
            mqttc.publish(
                topic_internal2, struct.pack("f", float(feed_into_grid)), qos=my_qos
            )
        elif msg.topic == topic_internal3:
            to_give = struct.unpack("f", msg.payload)[0]
            get_from_grid = self.give_charge(to_give)
            mqttc.publish(
                topic_internal4, struct.pack("f", float(get_from_grid)), qos=my_qos
            )

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

    def update(self, *args):
        pkd_charge = struct.pack("f", self.charge)
        _ = self.mqttc.publish(self.topic, pkd_charge, qos=my_qos)
        print(f"{time.time()}\t{__name__}\tPub on '{self.topic}': {self.charge}")
