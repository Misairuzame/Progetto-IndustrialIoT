import datetime
import json
import os
import sys

import plotille

"""
Uso: python plot_plotille.py [path/to/log.ndjson]
"""

log_file_path = "log.ndjson"
if len(sys.argv) > 1:
    log_file_path = sys.argv[1]

with open(log_file_path) as f:
    lines = f.readlines()

timestamps = []
metrics = {
    "panels.total": [],
    "batteries.total-charge": [],
    "elmeter.consumption-grid": [],
    "elmeter.feeding": [],
    "elmeter.consumption-required": [],
}

# Parsing dei dati
for line in lines:
    try:
        entry = json.loads(line)

        telemetry = entry["telemetry"]

        timestamps.append(datetime.datetime.fromtimestamp(telemetry["timestamp"]))
        metrics["panels.total"].append(telemetry["panels"]["total"])
        metrics["batteries.total-charge"].append(telemetry["batteries"]["total-charge"])
        metrics["elmeter.consumption-grid"].append(
            telemetry["elmeter"]["consumption-grid"]
        )
        metrics["elmeter.feeding"].append(telemetry["elmeter"]["feeding"])
        metrics["elmeter.consumption-required"].append(
            telemetry["elmeter"]["consumption-required"]
        )
    except:
        pass

# Grafico
fig = plotille.Figure()
fig.width = int(os.getenv("PLOT_WIDTH", 200))
fig.height = int(os.getenv("PLOT_HEIGHT", 25))
fig.set_y_limits(min_=0)
fig.set_x_limits(min_=min(timestamps), max_=max(timestamps))
fig.color_mode = "byte"
fig.y_label = "Valore"
fig.x_label = "Timestamp"
# fig.set_x_ticks(5)

# Colori: https://www.ditig.com/256-colors-cheat-sheet

# Produzione totale dei pannelli
panels_total = metrics["panels.total"]
min_len = min(len(timestamps), len(panels_total))
fig.plot(
    timestamps[:min_len],
    panels_total[:min_len],
    label="panels.total",
    lc=2,
)

# Carica delle batterie
batteries_total_charge = metrics["batteries.total-charge"]
min_len = min(len(timestamps), len(batteries_total_charge))
fig.plot(
    timestamps[:min_len],
    batteries_total_charge[:min_len],
    label="batteries.total-charge",
    lc=6,
)

# Prelievo di corrente dalla rete
elmeter_consumption_grid = metrics["elmeter.consumption-grid"]
min_len = min(len(timestamps), len(elmeter_consumption_grid))
fig.plot(
    timestamps[:min_len],
    elmeter_consumption_grid[:min_len],
    label="elmeter.consumption-grid",
    lc=9,
)

# Inserimento di corrente in rete
elmeter_feeding = metrics["elmeter.feeding"]
min_len = min(len(timestamps), len(elmeter_feeding))
fig.plot(
    timestamps[:min_len],
    elmeter_feeding[:min_len],
    label="elmeter.feeding",
    lc=12,
)

# Consumo della casa
elmeter_consumption_required = metrics["elmeter.consumption-required"]
min_len = min(len(timestamps), len(elmeter_consumption_required))
fig.plot(
    timestamps[:min_len],
    elmeter_consumption_required[:min_len],
    label="elmeter.consumption-required",
    lc=13,
)

print(fig.show(legend=True))
