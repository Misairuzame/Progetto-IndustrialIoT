import math
from datetime import datetime, timedelta


def solar_power_with_season(dt: datetime) -> float:
    # giorno dell'anno (1-365)
    day_of_year = dt.timetuple().tm_yday

    # durata del giorno in ore (approssimata)
    daylight_hours = 8 + 4 * math.sin(2 * math.pi * (day_of_year - 80) / 365)

    # ora del giorno
    hour = dt.hour + dt.minute / 60

    # centro e larghezza della "campana"
    center = 12
    sigma = daylight_hours / 6

    # produzione solo durante le ore di luce
    if (hour < center - daylight_hours / 2) or (hour > center + daylight_hours / 2):
        return 0

    # funzione gaussiana centrata a mezzogiorno con ampiezza stagionale
    return math.exp(-((hour - center) ** 2) / (2 * sigma**2))


def calcola_produzione_pannello(
    start_time: datetime,
    end_time: datetime,
    max_panel_production: int,
    step_minutes: int = 1,
) -> float:
    """
    Calcola la produzione totale del pannello tra due istanti (in Wh).
    La funzione integra numericamente la curva di produzione solare.

    :param start_time: inizio (datetime)
    :param end_time: fine (datetime)
    :param max_panel_production: produzione massima del pannello in Wh
    :param step_minutes: risoluzione (es. 1 min = integrazione più fine)
    :return: produzione in Wh
    """
    if end_time <= start_time:
        return 0.0

    total_production = 0.0
    step = timedelta(minutes=step_minutes)
    current_time = start_time

    while current_time < end_time:
        # Calcola produzione istantanea
        # * max_panel_production così scaliamo in modo che vada da 0 a max_panel_production
        inst_power_wh = solar_power_with_season(current_time) * max_panel_production

        # Calcola energia per questo intervallo e somma
        energy_wh = inst_power_wh * (step_minutes / 60)
        total_production += energy_wh

        current_time += step

    return total_production
