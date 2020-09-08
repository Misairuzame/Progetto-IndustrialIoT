import requests
import json
import matplotlib.pyplot as plt
import numpy as np

clientids = []

url = "http://localhost:9200/test4/_search"
headers = {"Content-type": "application/json"}
body = {
	"_source": ["clientinfo.clientid"],
	"query": {
    "bool": {
      "must": [
      	{
      		"exists": {
      			"field": "clientinfo.clientid"
      		}
      	}
      ]
    }
  },
  "size": 10000
}

r = requests.post(url, headers=headers, json=body)

hits = r.json()["hits"]["hits"]

for hit in hits:
    clientids.append(hit["_source"]["clientinfo"]["clientid"])

for clientid in clientids:
    y = []
    z = []
    w = []
    t = []
    u = []
    f = []
    p1_power = 0

    with open('log.ndjson', 'r') as logfile:
        line = logfile.readline()
        json_obj = json.loads(line)
        try:
            if(json_obj["clientid"] == clientid):
                y.append(json_obj["telemetry"]["batteries"]["total-charge"])
                z.append(json_obj["telemetry"]["elmeter"]["consumption-required"])
                w.append(json_obj["telemetry"]["elmeter"]["consumption-grid"])
                t.append(json_obj["telemetry"]["panels"]["total"])
                f.append(json_obj["telemetry"]["elmeter"]["feeding"])
                #u.append(json_obj["telemetry"]["panels"]["p1"])
                #p1_power += int(json_obj["telemetry"]["panels"]["p1"])
        except:
            pass
        while (len(line) > 0):
            json_obj = json.loads(line)
            try:
                if(json_obj["clientid"] == clientid):
                    y.append(json_obj["telemetry"]["batteries"]["total-charge"])
                    z.append(json_obj["telemetry"]["elmeter"]["consumption-required"])
                    w.append(json_obj["telemetry"]["elmeter"]["consumption-grid"])
                    t.append(json_obj["telemetry"]["panels"]["total"])
                    f.append(json_obj["telemetry"]["elmeter"]["feeding"])
                    #u.append(json_obj["telemetry"]["panels"]["p1"])
                    #p1_power += int(json_obj["telemetry"]["panels"]["p1"])
            except:
                pass
            line = logfile.readline()

    #print("Wh totali prodotti dal pannello p1: {}".format(p1_power))
        
    x = np.linspace(0, len(y), num=len(y))

    line1, = plt.plot(x, y, '-o', color='royalblue', label="Batteries charge") # Carica del sistema di accumulo
    line2, = plt.plot(x, z, '-o', color='firebrick', label="House consumption") # Consumo della casa
    line3, = plt.plot(x, w, '-o', color='dimgrey', label="Power from grid") # Energia presa dalla rete
    line4, = plt.plot(x, t, '-o', color='limegreen', label="Total solar panels") # Produzione totale pannelli solari
    #line5, = plt.plot(x, u, '-o', color='magenta', label="Panel 'p1' production") # Produzione pannello p1
    line6, = plt.plot(x, f, '-o', color='aqua', label="Feeding into grid") # Immissione in rete (feeding)
    plt.title(clientid)
    plt.plot()
    plt.legend()
    plt.show()
