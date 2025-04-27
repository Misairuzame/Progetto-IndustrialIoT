import time

import matplotlib.pyplot as plt
import my_functions

import time_scaling

time_start = time.time()
time_scale = time_scaling.get_time_scale()
xs = []
ys = []
counter = 0
try:
    while time.time() < (time_start + time_scale):
        now = time_scaling.get_scaled_time()
        cons = my_functions.consumption_function(now)
        print(str(now) + " => " + str(cons))
        counter += 1
        xs.append(now)
        ys.append(cons)
        time.sleep(5)
    print("Numero misurazioni in 1 giorno simulato: " + str(counter))
    plt.scatter(xs, ys)
    plt.show()
except KeyboardInterrupt:
    print("Numero misurazioni in 1 giorno simulato: " + str(counter))
    plt.scatter(xs, ys)
    plt.show()
