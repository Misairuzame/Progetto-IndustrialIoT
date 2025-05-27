import asyncio
import struct
import time
import uuid

import paho.mqtt.client as mqtt
from mqtt_topics import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="yellow")


my_qos = 2


class Inverter:
    def __init__(self, start_time, num_of_panels, port=1883):
        self.start_time = start_time
        self.num_of_panels = num_of_panels
        self.total_panels = 0

        self.recv_list = [asyncio.Event() for _ in range(self.num_of_panels)]

        mqtt_name = "pub-inverter-"
        mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_name)]
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_name + mqtt_rand_id,
        )
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.mqttc.connect("localhost", port, 60)

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(all_topics_panel, qos=my_qos)

    def on_message(self, mqttc, obj, msg):
        recv_panel = int(msg.topic.replace("telemetry/panel/p", ""))
        panel_prod = struct.unpack("f", msg.payload)[0]
        self.total_panels += panel_prod
        # Gli ID dei pannelli partono da 1, ma gli indici partono da 0.
        self.loop.call_soon_threadsafe(self.recv_list[recv_panel - 1].set)

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        await asyncio.gather(*(e.wait() for e in self.recv_list))

        total_panels = struct.pack("f", self.total_panels)
        _ = self.mqttc.publish(topic_internal_totalpanels, total_panels, qos=my_qos)
        print(f"Pub on '{topic_internal_totalpanels}': {self.total_panels}")

        for e in self.recv_list:
            e.clear()
        self.total_panels = 0
