import asyncio
import os
import random
import re
from datetime import datetime, timedelta

import charge_controller
import electric_panel
import house_consumption
import inverter
import meteo_manager
import solar_panel
import subscriber
from time_manager import TimeManager


def parse_hours_minutes(time_str: str):
    matches = re.findall(
        r"(\d+)\s*(hour|hours|minute|minutes)", time_str, re.IGNORECASE
    )

    hours = 0
    minutes = 0

    for value, unit in matches:
        if "hour" in unit.lower():
            hours += int(value)
        elif "minute" in unit.lower():
            minutes += int(value)

    return timedelta(hours=hours, minutes=minutes)


async def main():
    # datetime(2025, 1, 1, 0, 0)
    simulation_start = datetime.strptime(
        os.getenv("SIMULATION_START", "2025-01-01 00:00"),
        "%Y-%m-%d %H:%M",
    )

    # timedelta(hours=1)
    simulation_step = parse_hours_minutes(os.getenv("SIMULATION_STEP", "1 hour"))

    # 5
    simulation_speed = float(os.getenv("SIMULATION_SPEED", 5.0))

    # 0
    simulation_how_many_steps = int(os.getenv("SIMULATION_HOW_MANY_STEPS", 0))

    # Inizializza il time manager
    tm = TimeManager(
        start=simulation_start,
        step=simulation_step,
        speed=simulation_speed,
    )

    # Crea i moduli
    # Gestore del meteo
    meteo_man = meteo_manager.MeteoManager()

    # Profilo di consumo della casa
    house_profile = house_consumption.ConsumptionProfile()

    # Quadro elettrico
    el_panel = electric_panel.ElectricPanel(simulation_start, house_profile)

    # Pannelli solari
    num_of_panels = 0

    # Produzione massima teorica dei pannelli in W
    max_panel_production = 400

    roll = random.random()

    # Scegliamo, con un po' di casualità, le dimensioni gli impianti fotovoltaici,
    # sia il numero di pannelli che la dimensione (coerente) del sistema di accumulo
    if roll < 0.45:
        # Da 2 kW a 3.2 kW
        num_of_panels = random.randint(5, 8)
        storage_capacity_wh = random.randint(3, 5)
    elif roll < 0.95:
        # Da 3.6 kW a 6 kW
        num_of_panels = random.randint(9, 15)
        storage_capacity_wh = random.randint(6, 10)
    else:
        # Da 6.4 kW a 8 kW
        num_of_panels = random.randint(16, 20)
        storage_capacity_wh = random.randint(11, 15)

    storage_capacity_kwh = storage_capacity_wh * 1000
    max_total_prod = max_panel_production * num_of_panels

    solar_panels = [
        solar_panel.SolarPanel(i, simulation_start, max_panel_production, meteo_man)
        for i in range(1, num_of_panels + 1)
    ]

    # Controller di carica
    char_contr = charge_controller.ChargeController(storage_capacity_kwh)

    # Subscriber (gateway)
    subscr = subscriber.Subscriber(
        simulation_start,
        num_of_panels,
        max_total_prod,
        storage_capacity_kwh,
    )

    # Inverter
    invert = inverter.Inverter(simulation_start, num_of_panels)

    # Iscrivi i moduli al time manager
    tm.subscribe(meteo_man)
    tm.subscribe(house_profile)
    tm.subscribe(char_contr)
    tm.subscribe(el_panel)
    for panel in solar_panels:
        tm.subscribe(panel)
    tm.subscribe(subscr)
    tm.subscribe(invert)

    # Avvia la simulazione (il parametro opzionale steps indica quanti step effettuare
    # della simulazione, se non viene passato è None e non c'è limite alla simulazione)
    await tm.run(steps=simulation_how_many_steps)


if __name__ == "__main__":
    asyncio.run(main())
