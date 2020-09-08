import charge_controller
import electric_panel
import panel_spawner
from multiprocessing import Process
import sys

### WIP ###

try:
    char_contr = Process(target=charge_controller)
    char_contr.start()
    el_pan = Process(target=electric_panel)
    el_pan.start()
    pan_spw = Process(target=panel_spawner)
    pan_spw.start()
except KeyboardInterrupt:
    print("House exiting...")
    sys.exit()