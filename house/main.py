import asyncio
import os
import random
import re
from datetime import datetime, timedelta

import charge_controller
import electric_panel
import inverter
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
    # Controller di carica
    char_contr = charge_controller.ChargeController()

    # Quadro elettrico
    el_panel = electric_panel.ElectricPanel(simulation_start)

    # Subscriber (gateway)
    subscr = subscriber.Subscriber()

    # Pannelli solari
    num_of_panels = 0

    r = random.random()

    if r < 0.65:
        num_of_panels = random.randint(4, 8)  # Impianto medio
    elif r < 0.95:
        num_of_panels = random.randint(9, 12)  # Grande impianto
    else:
        num_of_panels = random.randint(13, 20)  # Impianto enorme / off-grid

    print(f"Spawning {num_of_panels} panels")
    solar_panels = [
        solar_panel.SolarPanel(i, simulation_start) for i in range(1, num_of_panels + 1)
    ]

    # Inverter
    invert = inverter.Inverter(simulation_start, num_of_panels)

    # Iscrivi i moduli al time manager
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
