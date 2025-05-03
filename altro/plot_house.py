import json
import sys

import matplotlib.pyplot as plt
import numpy as np

y = []
z = []
w = []
t = []
u = []
f = []
p1_power = 0

clientid = None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        clientid = sys.argv[1]
    with open("../log.ndjson", "rt") as logfile:
        for line in logfile:
            json_obj = json.loads(line)
            try:
                if clientid and json_obj["clientid"] == clientid:
                    y.append(json_obj["telemetry"]["batteries"]["total-charge"])
                    z.append(json_obj["telemetry"]["elmeter"]["consumption-required"])
                    w.append(json_obj["telemetry"]["elmeter"]["consumption-grid"])
                    t.append(json_obj["telemetry"]["panels"]["total"])
                    f.append(json_obj["telemetry"]["elmeter"]["feeding"])
                    # u.append(json_obj["telemetry"]["panels"]["p1"])
                    # p1_power += int(json_obj["telemetry"]["panels"]["p1"])
                else:
                    y.append(json_obj["telemetry"]["batteries"]["total-charge"])
                    z.append(json_obj["telemetry"]["elmeter"]["consumption-required"])
                    w.append(json_obj["telemetry"]["elmeter"]["consumption-grid"])
                    t.append(json_obj["telemetry"]["panels"]["total"])
                    f.append(json_obj["telemetry"]["elmeter"]["feeding"])
                    # u.append(json_obj["telemetry"]["panels"]["p1"])
                    # p1_power += int(json_obj["telemetry"]["panels"]["p1"])
            except:
                pass

    # print("Wh totali prodotti dal pannello p1: {}".format(p1_power))

    print(
        "Len(y): {}, Len(z): {}, Len(w): {}, Len(t): {}, Len(f): {}".format(
            len(y), len(z), len(w), len(t), len(f)
        )
    )

    min_len = np.min([len(y), len(z), len(w), len(t), len(f)])
    print("Min len: {}".format(min_len))

    y = y[:min_len]
    z = z[:min_len]
    w = w[:min_len]
    t = t[:min_len]
    f = f[:min_len]

    x = np.linspace(0, stop=min_len, num=min_len)

    # Carica del sistema di accumulo
    (line1,) = plt.plot(x, y, "-", color="royalblue", label="Batteries charge")
    # Consumo della casa
    (line2,) = plt.plot(x, z, "-", color="dimgrey", label="House consumption")
    # Energia presa dalla rete
    (line3,) = plt.plot(x, w, "-", color="firebrick", label="Power from grid")
    # Produzione totale pannelli solari
    (line4,) = plt.plot(x, t, "-", color="aqua", label="Total solar panels")
    # Produzione pannello p1
    # line5, = plt.plot(x, u, '-', color='magenta', label="Panel 'p1' production")
    # Immissione in rete (feeding)
    (line6,) = plt.plot(x, f, "-", color="limegreen", label="Feeding into grid")
    plt.plot()
    plt.legend()
    plt.show()
