import datetime
import random
import time

from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="blue")


class MeteoManager:
    def __init__(self):
        # 0 = totalmente sereno
        # 100 = totalmente coperto, produzione nulla
        self.nuvolosita_attuale = 0
        self.last_update = datetime.datetime(datetime.MINYEAR, 1, 1, 0, 0)
        self.started = False

    def get_meteo(self):
        return self.nuvolosita_attuale

    def __update_meteo(self):
        roll = random.random()
        if roll < 0.05:
            # 5 % di probabilità che sia un temporale molto forte
            nuvolosita = random.uniform(85, 99)
        elif roll < 0.20:
            # 15 % di probabilità che sia mediamente nuvoloso
            nuvolosita = random.uniform(40, 70)
        elif roll < 0.80:
            # 60% giornata con nuvolosità casuale con bias verso il sole
            nuvolosita = random.triangular(0, 40, 5)
        else:
            # 20% di probabilità che sia completamente sereno
            nuvolosita = 0

        self.nuvolosita_attuale = int(nuvolosita)

    async def update(self, **kwargs):
        # Al primo update aggiorna sempre il meteo
        if not self.started:
            self.__update_meteo()
            self.started = True
            return

        now: datetime.datetime = kwargs.get("current_time")

        # Calcolo il meteo per una giornata intera, le chiamate
        # dello stesso giorno ma in orari diversi restituiranno
        # tutte lo stesso meteo
        if now.day > self.last_update.day:
            self.__update_meteo()
            self.last_update = now

        print(f"Nuvolosità attuale: {self.nuvolosita_attuale}")
