import random
import struct
import sys
import time
import uuid

import paho.mqtt.client as mqtt

mqttc = None
topic_internal1 = "internal/totalpanels"
topic_internal2 = "internal/tofeed"
topic_internal3 = "internal/getfrombatteries"
topic_internal4 = "internal/getfromgrid"

# Unità di misura: Wh. Il sistema di accumulo di ogni casa
# viene scelto casualmente fra 5 e 12 kWh.
max_charge_wh = random.randint(5, 12) * 1000

# Per la simulazione, mettiamo come valore iniziale della carica un valore alto
charge = 0.75 * max_charge_wh

produced_now = 0

my_qos = 2


def give_charge(to_give: int) -> int:
    """
    Scarica le batterie per fornire l'energia richiesta alla casa, se possibile.

    Se le batterie possono fornire tutta l'energia
    che serve in un certo istante, allora lo fanno,
    decrementando la variabile che traccia quanta carica
    contengono e restituendo la potenza fornita. Se non
    possono fornirla tutta, allora (per semplicità) non
    forniscono alcuna carica.

    Args:
        to_give: Quanta carica prelevare dalle batterie.

    Returns:
        0 se tutta la carica richiesta è stata fornita dalle batterie,
        altrimenti la carica da prelevare dalla rete (per semplicità,
        tutta quella richiesta).
    """

    global charge

    if (charge - to_give) < 0:
        return to_give
    else:
        charge -= to_give
        return 0


def charge_batteries(to_charge: int) -> int:
    """
    Carica le batterie del valore passato, se possibile.

    Se le batterie possono contenere tutta l'energia che
    gli viene mandata in un istante, allora si caricano,
    sennò verrà fornita alla rete.

    Args:
        to_charge: Quanta carica inserire nelle batterie.

    Returns:
        0 se tutta la carica è stata inserita nelle batterie,
        altrimenti la carica che non c'è stata (per semplicità,
        tutta quella richiesta).
    """

    global charge

    if (charge + to_charge) > max_charge_wh:
        return to_charge
    else:
        charge += to_charge
        return 0


def on_connect(mqttc, obj, flags, rc):
    global topic_internal1, topic_internal2, topic_internal3, topic_internal4
    mqttc.subscribe(topic_internal1, qos=my_qos)
    mqttc.subscribe(topic_internal2, qos=my_qos)
    mqttc.subscribe(topic_internal3, qos=my_qos)
    mqttc.subscribe(topic_internal4, qos=my_qos)


def on_message(mqttc, obj, msg):
    global produced_now
    if msg.topic == topic_internal1:
        produced_now = struct.unpack("f", msg.payload)[0]
        feed_into_grid = charge_batteries(produced_now)
        mqttc.publish(
            topic_internal2, struct.pack("f", float(feed_into_grid)), qos=my_qos
        )
    elif msg.topic == topic_internal3:
        to_give = struct.unpack("f", msg.payload)[0]
        get_from_grid = give_charge(to_give)
        mqttc.publish(
            topic_internal4, struct.pack("f", float(get_from_grid)), qos=my_qos
        )


if __name__ == "__main__":
    port = 1883
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    mqtt_client_name = "pub-charcontr-"
    mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
    mqttc = mqtt.Client(client_id=mqtt_client_name + mqtt_rand_id)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect

    mqttc.connect("localhost", port, 60)
    mqttc.loop_start()

    try:
        topic = "telemetry/chargecontroller/c1"
        while True:
            pkd_charge = struct.pack("f", charge)
            (rc, mid) = mqttc.publish(topic, pkd_charge, qos=my_qos)
            print(f"{time.time()}\tPub on '{topic}': {charge} {mid} Rc: {rc}")
            time.sleep(5)
    except KeyboardInterrupt:
        mqttc.disconnect()
        time.sleep(1)
        print("Charge controller exiting...")
        sys.exit()
