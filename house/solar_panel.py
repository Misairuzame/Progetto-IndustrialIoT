import datetime
import random
import struct
import time
import uuid

import meteo_info
import my_functions
import paho.mqtt.client as mqtt
from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="green")


my_qos = 2


class SolarPanel:
    """
    Questa classe modella il comportamento di un singolo pannello solare.
    Si dovranno creare più istanze di questa classe per modellare un impianto
    composto da più pannelli solari.
    """

    def __init__(self, panel_id, start_time, port=1883):
        self.panel_id = panel_id
        self.max_panel_production = 250
        self.start_time = start_time

        mqtt_client_name = "pub-panel" + str(self.panel_id) + "-"
        mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
        self.mqttc = mqtt.Client(client_id=mqtt_client_name + mqtt_rand_id)

        self.mqttc.connect("localhost", port, 60)
        self.topic = "telemetry/panel/p" + str(self.panel_id)
        self.mqttc.loop_start()

        self.started = False

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
        # Se meteo_info.get_meteo...() fornisce quanta percentuale di
        # nuvole ci sono, (100-meteo_info...) può significare, in prima approssimazione,
        # "quanto sole c'è", e quindi, quanto può produrre un pannello solare.
        # Inoltre si moltiplica per un valore casuale per rendere i dati un po' più
        # differenziati fra loro.
        power = (
            my_functions.calcola_produzione_pannello(
                self.start_time, now, self.max_panel_production
            )
            * random.uniform(0.8, 1)
            * ((100 - meteo_info.get_meteo_internal()) / 100)
        )

        pkd_power = struct.pack("f", power)
        _ = self.mqttc.publish(self.topic, pkd_power, qos=my_qos)
        print(f"Pub on '{self.topic}': {power}")

        self.start_time = now
