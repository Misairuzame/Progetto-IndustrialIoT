import random
from datetime import datetime, timedelta

import charge_controller
import electric_panel
import solar_panel
import subscriber
from time_manager import TimeManager

simulation_start = datetime(2025, 1, 1, 0, 0)

# Inizializza il time manager
tm = TimeManager(start=simulation_start, dt=timedelta(hours=1), speed=5)

# Crea i moduli
# Controller di carica
char_contr = charge_controller.ChargeController()

# Quadro elettrico
el_panel = electric_panel.ElectricPanel(simulation_start)

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

# Iscrivi i moduli al time manager
tm.subscribe(char_contr)
tm.subscribe(el_panel)
for panel in solar_panels:
    tm.subscribe(panel)
tm.subscribe(subscriber)

# Avvia la simulazione (il parametro opzionale steps indica quanti step effettuare
# della simulazione, se non viene passato è None e non c'è limite alla simulazione)
tm.run()
