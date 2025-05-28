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

consumo_orario_kw = [
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

# Queste funzioni modellano l'andamento nel tempo del
# consumo elettrico tipico di una abitazione e della
# produzione tipica di un pannello solare


def consumo_istantaneo_orario_interpolato(ora_frazionaria: float) -> float:
    """
    Calcola il consumo istantaneo interpolando linearmente tra i valori nella lista `consumo_orario_kw`.

    :param ora_frazionaria: orario come numero decimale, es. 13.5 per 13:30
    :return: consumo istantaneo in Wh
    """
    h0 = int(ora_frazionaria) % 24
    h1 = (h0 + 1) % 24
    frazione = ora_frazionaria - h0

    return (
        consumo_orario_kw[h0]
        + (consumo_orario_kw[h1] - consumo_orario_kw[h0]) * frazione
    )


def calcola_consumo_intervallo(
    start_time: datetime,
    end_time: datetime,
    house_profile,
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

        # Shift casuale in avanti o all'indietro dell'orario per aumentare randomicità
        ora_frazionaria = house_profile.adjust_hour(
            current_time.hour + current_time.minute / 60
        )

        consumo_ist = consumo_istantaneo_orario_interpolato(ora_frazionaria)

        # Fattore costante (giorno per giorno) che aumenta o diminuisce il consumo,
        # sempre per aggiungere randomicità
        consumo_ist *= house_profile.get_daily_factor()

        consumo_totale += consumo_ist * durata_ore

        current_time = next_time

    return consumo_totale
