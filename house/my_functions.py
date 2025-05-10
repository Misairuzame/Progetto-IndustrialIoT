import math
import random
from datetime import datetime, timedelta

"""
How Many Watts Does a House Use Per Day, Month, and Year?
The average energy consumption per household is around 800 to 1,000 kilowatts-hour per month,
totaling approximately 9,600 to 12,000 kWh annually. When divided by the number of days in a year,
this translates to an average daily energy consumption of about 26 to 33 kWh. 

The average electricity rate in the US is about 16.6 cents per kWh, so, for a daily 26 to 33 kWh
energy use, the electricity bill should be $4.32 to $5.48 per day, $132.8 to $166 per month, and
$1593.6 to $1992 per year.
"""

y_kWh = [
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

y = [
    500,  # 0:00
    500,
    450,
    400,
    380,  # 4:00
    360,
    380,
    580,
    1000,  # 8:00
    1180,
    580,
    380,
    360,  # 12:00
    350,
    340,
    320,
    370,  # 16:00
    400,
    720,
    1220,
    1700,  # 20:00
    1720,
    1170,
    750,
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


def solar_power_function(hour: float):
    if 0 <= hour <= 24:
        hour = hour / 2
        return (
            12
            / math.sqrt(((2 * math.pi) * 1.06**2))
            * math.exp(((-((hour - 6) ** 2))) / ((2 * 1.06**2)))
        )
        # Il massimo è circa uguale a 4.5
    return 0


# Molto interessante (per ora inutilizzato)
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
        hour_float = current_time.hour + current_time.minute / 60

        # Mettiamo un po' di randomicità nelle ore, in modo da shiftare un po'
        # il consumo di energia della casa (sennò i picchi sono sempre nelle stesse ore)
        # hour_float = (hour_float + random.gauss(0, 5)) % 24
        # Per uso con la funzione stagionale usare timedelta(hours=random.gauss(...));
        # aggiungere anche minuti come una round della (parte frazionaria * 60)

        # * (max_panel_production / 4.5) è perchè la funzione che modella la produzione
        # del singolo pannello solare va da 0 a 4.5, in questo modo la scaliamo in modo
        # che vada da 0 a max_panel_production
        inst_power_Wh = solar_power_function(hour_float) * (max_panel_production / 4.5)

        # Calcola energia per questo intervallo e somma
        energy_Wh = inst_power_Wh * (step_minutes / 60)
        total_production += energy_Wh

        current_time += step

    return total_production


def consumo_istantaneo_orario_interpolato(ora_frazionaria: float) -> float:
    """
    Calcola il consumo istantaneo interpolando linearmente tra i valori nella lista `y`.

    :param ora_frazionaria: orario come numero decimale, es. 13.5 per 13:30
    :return: consumo istantaneo in Wh
    """
    h0 = int(ora_frazionaria) % 24
    h1 = (h0 + 1) % 24
    frazione = ora_frazionaria - h0

    return y[h0] + (y[h1] - y[h0]) * frazione


def calcola_consumo_intervallo(
    start_time: datetime,
    end_time: datetime,
    step_minutes: int = 1,
) -> float:
    """
    Calcola il consumo totale integrando a piccoli passi e interpolando i consumi orari.

    :param start_time: datetime inizio
    :param end_time: datetime fine
    :param step_minutes: passo temporale per l'integrazione (default: 1 minuto)
    :return: consumo in Wh
    """
    if end_time <= start_time:
        return 0.0

    consumo_totale = 0.0
    current_time = start_time
    step = timedelta(minutes=step_minutes)

    while current_time < end_time:
        next_time = min(current_time + step, end_time)
        durata_ore = (next_time - current_time).total_seconds() / 3600
        ora_frazionaria = current_time.hour + current_time.minute / 60

        consumo_ist = consumo_istantaneo_orario_interpolato(ora_frazionaria)
        consumo_totale += consumo_ist * durata_ore

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
    print(f"Consumo dalle 17:00 alle 18:00: {consumo_17_18} Wh")
    print(f"Consumo dalle 19:30 alle 20:00: {consumo_1930_2000} Wh")
    print(f"Consumo dalle 23:30 alle 00:30: {consumo_cross} Wh")

    start = datetime(2024, 1, 1, 19, 30)  # 19:30
    end = datetime(2024, 1, 1, 21, 15)  # 21:15
    print(
        f"Consumo stimato 19:30 - 21:15: {calcola_consumo_intervallo(start, end)=} Wh"
    )

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 2, 0, 0)
    print(f"Consumo stimato 24h: {calcola_consumo_intervallo(start, end)=} Wh")

    start = datetime(2024, 1, 1, 14, 13)
    end = datetime(2024, 1, 2, 14, 13)
    print(f"Consumo stimato 24h (2): {calcola_consumo_intervallo(start, end)=} Wh")

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 2, 0, 0)
    step = timedelta(hours=1)
    nxt = start
    curr = start
    tot = 0
    while curr < end:
        nxt += step
        tot += calcola_consumo_intervallo(curr, nxt)
        curr = nxt
    print(f"Consumo stimato 24h (3): {tot=}")

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 8, 0, 0)
    print(f"Consumo stimato 1 settimana: {calcola_consumo_intervallo(start, end)=} Wh")

    start = datetime(2024, 1, 1, 0, 0)
    end = datetime(2024, 1, 8, 0, 0)
    step = timedelta(hours=1)
    nxt = start
    curr = start
    tot = 0
    while curr < end:
        nxt += step
        tot += calcola_consumo_intervallo(curr, nxt)
        curr = nxt
    print(f"Consumo stimato 1 settimana (2): {tot=}")

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
    from matplotlib.animation import FuncAnimation

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

    # Creazione dell'array di ore durante il giorno
    ore = np.arange(0, 24, 0.1)

    # Creazione della figura e degli assi
    fig, ax = plt.subplots(figsize=(10, 5))
    (line,) = ax.plot([], [], label="Produzione solare", color="orange")
    date_text = ax.text(
        0.95,
        0.95,
        "",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        color="black",
    )
    ax.set_title("Produzione solare durante l'anno")
    ax.set_xlabel("Ora del giorno")
    ax.set_ylabel("Produzione normalizzata (≈kW)")
    ax.grid(True)
    ax.legend()
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 5)

    # Funzione di inizializzazione (per l'animazione)
    def init():
        line.set_data([], [])
        date_text.set_text("")
        return (line,)

    # Funzione di aggiornamento per l'animazione
    def update(frame):
        # 'frame' rappresenta il giorno dell'anno (partiamo dal primo giorno)
        # Giorni nell'anno (modulo 365 per farlo ripetere ogni anno)
        giorno = frame % 365

        # Creiamo un datetime per il primo giorno dell'anno
        start_date = datetime(2025, 1, 1)

        # Calcoliamo la data del giorno corrente
        current_day = start_date + timedelta(days=giorno.item())

        # Calcoliamo la produzione per tutte le ore del giorno dato il giorno dell'anno
        produzione = [
            solar_power_with_season(
                current_day.replace(hour=int(h), minute=int((h % 1) * 60))
            )
            for h in ore
        ]

        # Aggiorna i dati della linea
        line.set_data(ore, produzione)

        # Aggiungi la data alla legenda
        # Formatta la data come "GG Mese AAAA"
        date_str = current_day.strftime("%d %b %Y")
        date_text.set_text(f"Data: {date_str}")

        return line, date_text

    # Crea l'animazione
    ani = FuncAnimation(
        fig, update, frames=np.arange(0, 365), init_func=init, blit=True, interval=100
    )

    # Mostra l'animazione
    plt.tight_layout()
    plt.show()

    # Genera 100 valori casuali con distribuzione gaussiana
    values = [random.gauss(0, 0.5) for _ in range(100)]

    # Crea il grafico
    plt.plot(values)
    plt.title("Distribuzione Gaussiana - 100 Valori")
    plt.xlabel("Indice")
    plt.ylabel("Valore")
    plt.grid(True)
    plt.show()
