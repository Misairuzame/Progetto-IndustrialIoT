import math
from datetime import datetime, timedelta

def solar_power_function(hour: float):
    if 0 <= hour <= 24:
        hour = hour / 2
        return (
            12
            / math.sqrt((2 * math.pi) * 1.06**2)
            * math.exp((-((hour - 6) ** 2)) / ((2 * 1.06**2)))
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

        # * (max_panel_production / 4.5) è perchè la funzione che modella la produzione
        # del singolo pannello solare va da 0 a 4.5, in questo modo la scaliamo in modo
        # che vada da 0 a max_panel_production
        inst_power_wh = solar_power_function(hour_float) * (max_panel_production / 4.5)

        # Calcola energia per questo intervallo e somma
        energy_wh = inst_power_wh * (step_minutes / 60)
        total_production += energy_wh

        current_time += step

    return total_production


if __name__ == "__main__":
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

    import random
    # Genera 100 valori casuali con distribuzione gaussiana
    values = [random.gauss(0, 0.5) for _ in range(100)]

    # Crea il grafico
    plt.plot(values)
    plt.title("Distribuzione Gaussiana - 100 Valori")
    plt.xlabel("Indice")
    plt.ylabel("Valore")
    plt.grid(True)
    plt.show()

    ##############################################################################

    # Original function parameters
    mu_orig = 6
    sigma_orig = 1.06
    A_orig = 12

    # Extended function parameters
    mu_ext = 12
    sigma_ext = 4
    peak_ext = 12

    # Generate x values
    hours = np.linspace(0, 24, 500)

    # Calculate y values for both functions
    original = [
        A_orig
        / math.sqrt(2 * math.pi * sigma_orig**2)
        * math.exp(-((h - mu_orig) ** 2) / (2 * sigma_orig**2))
        for h in hours
    ]

    extended = [
        peak_ext * math.exp(-((h - mu_ext) ** 2) / (2 * sigma_ext**2)) for h in hours
    ]

    sigma = 4
    mu = 12
    A = 12
    other = [
        A
        / (math.sqrt(2 * math.pi) * sigma)
        * math.exp(-((h - mu) ** 2) / (2 * sigma**2))
        for h in hours
    ]

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(
        hours, original, label="Original Gaussian (center=6, σ=1.06)", linestyle="--"
    )
    plt.plot(hours, extended, label="Extended Gaussian (center=12, σ=4)", linestyle="-")
    plt.plot(hours, extended, label="Extended Gaussian (stessa area)", linestyle="-")
    plt.title("Confronto tra Gaussiana Originale e Allargata")
    plt.xlabel("Ora del giorno")
    plt.ylabel("Valore della funzione")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
