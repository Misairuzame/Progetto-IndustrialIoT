import math
from datetime import datetime, timedelta

y = [
    0.5,  # 0:00
    0.5,
    0.45,
    0.4,
    0.38,  # 4:00
    0.36,
    0.38,
    0.58,
    1,  # 8:00
    1.18,
    0.58,
    0.38,
    0.36,  # 12:00
    0.35,
    0.34,
    0.32,
    0.37,  # 16:00
    0.4,
    0.72,
    1.22,
    1.7,  # 20:00
    1.72,
    1.17,
    0.75,
]

# Secondo GPT.....
y_realistico = [
    0.3,  # 00:00 - 1:00 (bassa, solo frigorifero e standby)
    0.3,  # 01:00 - 2:00 (bassa, solo frigorifero e standby)
    0.3,  # 02:00 - 3:00 (bassa, solo frigorifero e standby)
    0.3,  # 03:00 - 4:00 (bassa, solo frigorifero e standby)
    0.4,  # 04:00 - 5:00 (bassa, solo frigorifero e standby)
    0.6,  # 05:00 - 6:00 (leggero aumento con riscaldamento/caffè, ecc.)
    1.0,  # 06:00 - 7:00 (un po' più alto per preparazione della colazione)
    1.2,  # 07:00 - 8:00 (preparazione colazione e prime attività domestiche)
    1.4,  # 08:00 - 9:00 (attività domestiche, luci, riscaldamento)
    0.7,  # 09:00 - 10:00 (bassa, casa vuota o semi-vuota)
    0.6,  # 10:00 - 11:00 (bassa, casa vuota o semi-vuota)
    0.6,  # 11:00 - 12:00 (bassa, casa vuota o semi-vuota)
    0.7,  # 12:00 - 13:00 (leggera attività, ma ancora basso)
    0.7,  # 13:00 - 14:00 (leggera attività, ma ancora basso)
    0.8,  # 14:00 - 15:00 (attività leggera, casa semi-vuota)
    0.8,  # 15:00 - 16:00 (attività leggera, casa semi-vuota)
    1.0,  # 16:00 - 17:00 (cominciano a tornare a casa, luci accese, TV)
    1.5,  # 17:00 - 18:00 (preparazione cena, uso più intenso)
    1.8,  # 18:00 - 19:00 (cena, cucine in uso, forno, frigorifero, luci)
    1.9,  # 19:00 - 20:00 (cena e post-cena, luci, TV, ecc.)
    1.5,  # 20:00 - 21:00 (relax, luci, TV, computer)
    1.2,  # 21:00 - 22:00 (relax, luci, TV, computer)
    1.0,  # 22:00 - 23:00 (attività leggere, luci)
    0.6,  # 23:00 - 00:00 (solo frigorifero e dispositivi in stand-by)
]

# Queste funzioni modellano l'andamento nel tempo del
# consumo elettrico tipico di una abitazione e della
# produzione tipica di un pannello solare


def consumption_function(x: int):
    """
    La funzione assume i valori di interesse nel dominio [0,12].
    Visto che le ore del giorno sono 24, se si vuole passare alla
    funzione un valore compreso fra 0 e 24 (l'ora del giorno),
    basterà poi dividere quel valore per 2, in modo da ottenere
    dei risultati significativi (fuori dal dominio la funzione
    restituisce valori completamente insensati).
    ^^^ TODO: È ancora così??? Verificare !!!

    Args:
        x: intero, l'ora del giorno attuale.
    """

    if 0 <= x <= 24:
        return y[round(x)]  # Massimo: 1.72
    return 0


def solar_power_function(x):
    if 0 <= x <= 24:
        x = x / 2
        return (
            12
            / math.sqrt(((2 * math.pi) * 1.06**2))
            * math.exp(((-((x - 6) ** (2)))) / ((2 * 1.06 ** (2))))
        )
        # Il massimo è circa uguale a 4.5
    return 0


# Molto interessante
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
    return 4.5 * math.exp(-((hour - center) ** 2) / (2 * sigma**2))


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
        hour_float = current_time.hour + current_time.minute / 60
        inst_power_kW = (
            solar_power_function(hour_float) * (max_panel_production / 4.5) / 1000
        )  # in kW

        # Calcola energia per questo intervallo e somma
        energy_wh = inst_power_kW * (step_minutes / 60) * 1000  # kW x h x 1000 = Wh
        total_production += energy_wh

        current_time += step

    return total_production


def calcola_consumo_intervallo(start_time: datetime, end_time: datetime) -> float:
    """
    Calcola il consumo energetico (in kWh) tra due istanti arbitrari.
    Assume consumo costante all'interno di ogni ora.

    :param start_time: datetime di inizio
    :param end_time: datetime di fine
    :return: consumo totale in kWh
    """
    if end_time <= start_time:
        return 0.0

    consumo_totale = 0.0
    current_time = start_time

    while current_time < end_time:
        next_time = min(
            (current_time + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            ),
            end_time,
        )
        durata_minuti = (next_time - current_time).total_seconds() / 60
        ora_corrente = current_time.hour

        consumo_ora = y[ora_corrente % 24]  # modulo 24 per sicurezza
        # proporzione di consumo orario
        consumo_totale += consumo_ora * (durata_minuti / 60)

        current_time = next_time

    return consumo_totale


if __name__ == "__main__":
    # Esempio di utilizzo
    start_time = datetime(2023, 5, 4, 17, 0)  # 17:00
    end_time = datetime(2023, 5, 4, 18, 0)  # 18:00

    start_time_1930 = datetime(2023, 5, 4, 19, 30)  # 19:30
    end_time_1930 = datetime(2023, 5, 4, 20, 0)  # 20:00

    start_time_cross = datetime(2023, 5, 4, 23, 30)  # 23:30
    end_time_cross = datetime(2023, 5, 5, 0, 30)  # 00:30 (crossover)

    # Calcolare il consumo dalle 17:00 alle 18:00
    consumo_17_18 = calcola_consumo_intervallo(start_time, end_time)

    # Calcolare il consumo dalle 19:30 alle 20:00
    consumo_1930_2000 = calcola_consumo_intervallo(start_time_1930, end_time_1930)

    # Calcolare il consumo dalle 23:30 alle 00:30 (crossover tra giorni)
    consumo_cross = calcola_consumo_intervallo(start_time_cross, end_time_cross)

    # Mostra i risultati
    print(f"Consumo dalle 17:00 alle 18:00: {consumo_17_18} kWh")
    print(f"Consumo dalle 19:30 alle 20:00: {consumo_1930_2000} kWh")
    print(f"Consumo dalle 23:30 alle 00:30: {consumo_cross} kWh")

    start = datetime(2024, 1, 1, 19, 30)  # 19:30
    end = datetime(2024, 1, 1, 21, 15)  # 21:15
    print(
        f"Consumo stimato 19:30 - 21:15: {calcola_consumo_intervallo(start, end)=} kWh"
    )

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 2, 0, 0)
    print(f"Consumo stimato 24h: {calcola_consumo_intervallo(start, end)=} kWh")

    start = datetime(2024, 1, 1, 14, 13)
    end = datetime(2024, 1, 2, 14, 13)
    print(f"Consumo stimato 24h (2): {calcola_consumo_intervallo(start, end)=} kWh")

    max_panel_production = 250

    inizio = datetime(2025, 5, 4, 10, 15)
    fine = datetime(2025, 5, 4, 14, 45)
    produzione = calcola_produzione_pannello(inizio, fine, max_panel_production)
    print(f"Produzione stimata 1 pannello 10:15 - 14:45: {produzione=} Wh")

    inizio = datetime(2025, 5, 4, 0, 0)
    fine = datetime(2025, 5, 5, 0, 0)
    produzione = calcola_produzione_pannello(inizio, fine, max_panel_production)
    print(f"Produzione stimata 1 pannello 24h: {produzione=} Wh")

    import matplotlib.pyplot as plt
    import numpy as np

    # Crea una lista di ore (es. 0.0, 0.1, ..., 24.0)
    ore = np.linspace(0, 24, 500)
    produzione = [solar_power_function(h) for h in ore]

    # Disegna il grafico
    plt.figure(figsize=(10, 5))
    plt.plot(ore, produzione, label="solar_power_function(x)", color="orange")
    plt.title("Produzione solare teorica durante il giorno")
    plt.xlabel("Ora del giorno")
    plt.ylabel("Produzione normalizzata (≈kW)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
