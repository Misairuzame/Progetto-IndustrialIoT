import random
import sys
from multiprocessing import Process

import single_panel

num_of_panels = random.randint(6, 20)
print("Spawning " + str(num_of_panels) + " panels")

processes = []

try:
    for i in range(1, num_of_panels + 1):
        aproc = Process(target=single_panel.my_main, args=(str(i),))
        processes.append(aproc)
        aproc.start()
    for proc in processes:
        proc.join()
except KeyboardInterrupt:
    print("Panel spawner exiting...")
    sys.exit()
