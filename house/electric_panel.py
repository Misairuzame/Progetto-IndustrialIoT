import datetime
import random
import struct
import time
import uuid

import my_functions
import paho.mqtt.client as mqtt

topic1 = "telemetry/electricpanel/consumption-grid"
topic2 = "telemetry/electricpanel/feeding"
topic3 = "telemetry/electricpanel/consumption-required"

topic_internal1 = "internal/tofeed"
topic_internal2 = "internal/getfrombatteries"
topic_internal3 = "internal/getfromgrid"

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
        self.mqttc.loop_start()

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_internal1, qos=my_qos)
        mqttc.subscribe(topic_internal2, qos=my_qos)
        mqttc.subscribe(topic_internal3, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        if msg.topic == topic_internal3:
            self.get_from_grid = struct.unpack("f", msg.payload)[0]
        elif msg.topic == topic_internal1:
            self.feed_into_grid = struct.unpack("f", msg.payload)[0]

    def update(self, *args):
        now: datetime.datetime = args[0]

        consumption_required = (
            my_functions.calcola_consumo_intervallo(self.start_time, now)
            * random.uniform(0.75, 1.25)  # Un po' di randomicità nel consumo
            * 1000  # Wh -> kWh
        )

        # Simulazione: il quadro elettrico "chiede" energia alle batterie, se è possibile le batterie
        # gliela forniscono tutta, sennò (per semplicità) non gliene forniscono alcuna e tutta la
        # corrente viene presa dalla rete elettrica.
        _ = self.mqttc.publish(
            topic_internal2, struct.pack("f", consumption_required), qos=my_qos
        )
        print(
            f"{time.time()}\t{__name__}\tPub on '{topic_internal2}': {consumption_required}"
        )

        pkd_consumption = struct.pack("f", self.get_from_grid)
        _ = self.mqttc.publish(topic1, pkd_consumption, qos=my_qos)
        print(f"{time.time()}\t{__name__}\tPub on '{topic1}': {self.get_from_grid}")

        pkd_feed = struct.pack("f", self.feed_into_grid)
        _ = self.mqttc.publish(topic2, pkd_feed, qos=my_qos)
        print(f"{time.time()}\t{__name__}\tPub on '{topic2}': {self.feed_into_grid}")

        pkd_consumption_req = struct.pack("f", consumption_required)
        _ = self.mqttc.publish(topic3, pkd_consumption_req, qos=my_qos)
        print(f"{time.time()}\t{__name__}\tPub on '{topic3}': {consumption_required}")

        self.start_time = now
