import asyncio
import struct
import time

import paho.mqtt.client as mqtt
from mqtt_config import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="yellow")


class Inverter:
    def __init__(self, start_time, num_of_panels):
        self.start_time = start_time
        self.num_of_panels = num_of_panels
        self.total_panels = 0

        self.recv_list = [asyncio.Event() for _ in range(self.num_of_panels)]

        mqtt_client_name = generate_client_name("pub-inverter")
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_name,
            clean_session=False,
        )
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

        self.mqttc.connect(mqtt_address, mqtt_port, 60)

        self.loop = asyncio.get_event_loop()

        self.mqttc.loop_start()

        self.started = False

    def on_connect(self, mqttc, obj, flags, rc, properties):
        mqttc.subscribe(topic_panels_wildcard, qos=mqtt_qos)

    def on_message(self, mqttc, obj, msg):
        recv_panel = int(msg.topic.replace(topic_panel_prefix, ""))
        panel_prod = struct.unpack("f", msg.payload)[0]
        self.total_panels += panel_prod
        # Gli ID dei pannelli partono da 1, ma gli indici partono da 0.
        self.loop.call_soon_threadsafe(self.recv_list[recv_panel - 1].set)

    def mqtt_publish(self, topic: str, payload: float):
        pack_and_publish(self.mqttc, topic, payload)
        print(f"Pub on '{topic}': {payload}")

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        await asyncio.gather(*(e.wait() for e in self.recv_list))

        self.mqtt_publish(topic_internal_totalpanels, self.total_panels)

        for e in self.recv_list:
            e.clear()
        self.total_panels = 0
