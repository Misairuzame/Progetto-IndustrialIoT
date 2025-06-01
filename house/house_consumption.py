import datetime
import random
import time

from print_color import print as color_print


def print(*args):
    color_print(f"{time.time()}\t{__name__}\t", *args, color="black", format="bold")


class ConsumptionProfile:
    def __init__(self):
        self.fattore_giornaliero = 1.0
        self.peak_shift = 0
        self.last_update = datetime.datetime(datetime.MINYEAR, 1, 1, 0, 0)
        self.started = False

    def __update_profile(self):
        self.fattore_giornaliero = random.uniform(0.7, 1.3)
        # self.peak_shift = random.gauss(0, 0.5)
        self.peak_shift = random.gauss(0, 1.5)

    def get_daily_factor(self) -> float:
        return self.fattore_giornaliero

    def get_peak_shift(self) -> float:
        return self.peak_shift

    def adjust_hour(self, hour: float) -> float:
        return (hour + self.peak_shift) % 24

    async def update(self, **kwargs):
        # Al primo update aggiorna sempre il profilo
        if not self.started:
            self.__update_profile()
            self.started = True
            return

        now: datetime.datetime = kwargs.get("current_time")

        # Calcolo il profilo di consumo della casa una volta
        # al giorno, le chiamate dello stesso giorno ma in
        # orari diversi restituiranno lo stesso profilo di
        # consumo
        if now.date() != self.last_update.date():
            self.__update_profile()
            self.last_update = now

        print(
            f"Fattore di consumo attuale: {self.fattore_giornaliero}, "
            f"Peak shift: {self.peak_shift}"
        )
