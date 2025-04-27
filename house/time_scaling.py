# In questo file si definisce "di quanto" scalare la
# durata di una giornata, in modo da non dover aspettare
# davvero 24 ore per vedere il funzionamento generale del
# sistema nell'arco di un giorno. La variabile time_scaling
# conterrà il numero di secondi reali che si vuole usare per
# indicare una giornata di 24 ore (simulata). Ad esempio, se
# la variabile assume il valore 300, allora si simulerà il
# passaggio di 24 ore (86400 secondi) in 5 minuti reali (300 secondi).
import time

time_scaling = 300


def get_time_scale():
    return time_scaling


def get_scaled_time():
    return time.time() % time_scaling / time_scaling * 24


def get_one_week_ago_scaled():
    """
    Una settimana normale in secondi = 604800
    (non utilizzato)
    """
    # normal_week_seconds = 604800
    return time.time() - (time_scaling * 7)
