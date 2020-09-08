import paho.mqtt.client as mqtt
import sys
import struct
import random
import time
import uuid

mqttc = None
topic_internal1 = "internal/totalpanels"
topic_internal2 = "internal/tofeed"
topic_internal3 = "internal/getfrombatteries"
topic_internal4 = "internal/getfromgrid"

max_charge_wh = 5000 # Unità di misura: Wh
# 1Wh = 1W * 1h = 1W * 3600s
# Visto che le misurazioni vengono
# inviate ogni 5 secondi, e sono in W (sarebbe W per 5 secondi),
# allora possiamo definire la carica massima
# come max_charge*Wh / (5s/3600s)
# Così otteniamo un valore in "W" (per 5 secondi)

#max_charge_w = max_charge_wh/(5/3600)
charge = 0.75*max_charge_wh # Per la simulazione, mettiamo come valore iniziale della carica un valore alto

produced_now = 0


my_qos = 2

def give_charge(to_give):
    """
    Se le batterie possono fornire tutta l'energia
    che serve in un certo istante, allora lo fanno,
    decrementando la variabile che traccia quanta carica
    contengono e restituendo la potenza fornita. Se non
    possono fornirla tutta, allora (per semplicità) non
    forniscono alcuna carica.
    """
    global charge
    if (charge-to_give) < (max_charge_wh*0.1):
        return to_give
    else:
        charge-=to_give
        return 0

def charge_batteries(to_charge):
    """
    Se le batterie possono contenere tutta l'energia che
    gli viene mandata in un istante, allora si caricano,
    sennò viene fornita alla rete.
    """
    global charge
    if (charge+to_charge) > (max_charge_wh*0.9): # Si caricano le batterie fino ad un massimo del 90%
        return to_charge
    else:
        charge+=to_charge
        return 0

def on_connect(mqttc, obj, flags, rc):
    #print("Connected with result code: " + str(rc))
    global topic_internal1, topic_internal2, topic_internal3, topic_internal4
    mqttc.subscribe(topic_internal1, qos=my_qos)
    mqttc.subscribe(topic_internal2, qos=my_qos)
    mqttc.subscribe(topic_internal3, qos=my_qos)
    mqttc.subscribe(topic_internal4, qos=my_qos)


def on_message(mqttc, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    global produced_now
    if msg.topic == topic_internal1:
        produced_now = struct.unpack('f', msg.payload)[0]
        feed_into_grid = charge_batteries(produced_now)
        mqttc.publish(topic_internal2, struct.pack('f', float(feed_into_grid)), qos=my_qos)
    elif msg.topic == topic_internal3:
        to_give = struct.unpack('f', msg.payload)[0]
        get_from_grid = give_charge(to_give)
        mqttc.publish(topic_internal4, struct.pack('f', float(get_from_grid)), qos=my_qos)


def on_publish(mqttc, obj, mid):
    #print("MsgId: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    #print("Subscribed: " + str(mid) + " " + str(granted_qos))
    pass


if __name__ == '__main__':
    port = 1883
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    mqtt_client_name = "pub-charcontr-"
    mqtt_rand_id = str(uuid.uuid4())[:23-len(mqtt_client_name)]
    mqttc = mqtt.Client(client_id=mqtt_client_name+mqtt_rand_id)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    
    mqttc.connect("localhost", port, 60)
    mqttc.loop_start()

    try:
        #start_time = time.time()
        while True:
            #start_time = time.time()
            topic = "telemetry/chargecontroller/c1"
            pkd_charge = struct.pack('f', charge)
            (rc, mid) = mqttc.publish(topic, pkd_charge, qos=my_qos)
            print(str(time.time())+"\tPub on '"+topic+"': "+str(charge)+" "+str(mid)+" Rc: "+str(rc))
            #while time.time() < (start_time+5):
                #pass
            time.sleep(5)
    except KeyboardInterrupt:
        mqttc.disconnect()
        time.sleep(1)
        print("Charge controller exiting...")        
        sys.exit()