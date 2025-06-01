import datetime
import random
import time

import paho.mqtt.client as mqtt
import solar_functions
from mqtt_config import *
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="green")


class SolarPanel:
    """
    Questa classe modella il comportamento di un singolo pannello solare.
    Si dovranno creare più istanze di questa classe per modellare un impianto
    composto da più pannelli solari.
    """

    def __init__(self, panel_id, start_time, max_panel_production, meteo_man):
        self.panel_id = panel_id
        self.start_time = start_time
        self.max_panel_production = max_panel_production
        self.meteo_man = meteo_man

        mqtt_client_name = generate_client_name(f"pub-panel{self.panel_id}")
        self.mqttc = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=mqtt_client_name,
            clean_session=False,
        )

        self.mqttc.connect(mqtt_address, mqtt_port, 60)
        self.topic = topic_panel_prefix + str(self.panel_id)
        self.mqttc.loop_start()

        self.started = False

    def mqtt_publish(self, topic: str, payload: float):
        pack_and_publish(self.mqttc, topic, payload)
        print(f"Pub on '{topic}': {payload}")

    async def update(self, **kwargs):
        # Salta il primo update per sincronizzarsi con tutti i dispositivi
        if not self.started:
            print("Skipping the first step to sync all devices...")
            self.started = True
            return

        # Viene inviato un dato float "grezzo", che si ritiene sia
        # preciso fino alla terza cifra decimale; dalla quarta in poi
        # verrà arrotondato dal subscriber.
        # Esempio: Viene inviato il dato grezzo 115.72652869419638.
        # La misurazione è accurata fino alla terza cifra decimale,
        # quindi è considerato attendibile 115.726; la quarta cifra
        # viene approssimata dal subscriber, che quindi utilizzerà come
        # dato per i passaggi successivi 115.7265.

        now: datetime.datetime = kwargs.get("current_time")

        power = solar_functions.calcola_produzione_pannello(
            self.start_time, now, self.max_panel_production
        )

        # Meteo
        power *= (100 - self.meteo_man.get_meteo()) / 100

        # Un po' di randomicità nella produzione
        power *= random.uniform(0.90, 1.00)

        # Randomicità "forte" con bassa probabilità, es. nuvola che passa
        # e se ne va velocemente
        power *= random.gauss(1.0, 0.02)

        self.mqtt_publish(self.topic, power)

        self.start_time = now
