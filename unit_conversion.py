# Utility di conversione per le
# unità di misura, es. kWh -> kW
# o Wh -> W
import time_scaling

def watt_instant_to_watth(watt_istant):
    """
    Le misurazioni vengono inviate ogni 5 secondi,
    e rappresentano i Watt che sono stati prodotti
    negli ultimi 5 secondi. Questo perchè possiamo
    assumere che in 5 secondi i Watt prodotti rimangano
    costanti. In questo modo, se la lettura della potenza
    istantanea è, ad esempio di 200W, allora in 5 secondi
    vengono prodotti 200W*5s. Per convertirli in Wh, unità
    di misura dell'energia, la formula è la seguente:
    1 Wh = 1 W * (#secondi)/3600
    In questo esempio si avrebbe che:
    200W * 5s => 200*5/3600 = 0,2778 Wh
    Nel caso si stia "scalando" il tempo, al fine della
    simulazione, i valori potrebbero non essere 100% realistici,
    visto che le misurazioni vengono mandate comunque ogni 5 secondi,
    ma 5 secondi reali corrispondono ad un tempo molto maggiore nella
    simulazione, e quindi l'approssimazione fatta non è completamente
    realistica (se ad esempio un giorno della simulazione corrisponde
    a 5 minuti reali, abbiamo scalato il tempo di un fattore 86400/300,
    quindi 5 secondi reali corrispondono a 60 secondi della simulazione).
    In una giornata di 24h (86400 secondi) avremmo 86400/5 ~ 17000 misurazioni,
    in una giornata "simulata" di 300 secondi (reali) avremo quindi
    300/5 = 60 misurazioni.
    """
    # one_simulated_hour = 3600*time_scaling.get_time_scale()/86400
    # semplificata, risulta:
    one_simulated_hour = (1/24)*time_scaling.get_time_scale()
    return watt_istant*5/one_simulated_hour

def watth_to_watt_instant(watth):
    one_simulated_hour = (1/24)*time_scaling.get_time_scale()
    return watth*one_simulated_hour/5

#def battery_wh_to_w(watth):
#   pass