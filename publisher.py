import paho.mqtt.client as mqtt
import sys
import struct
import random
import time

# ------------------------------------ #
# !!!File usato solo durante i test!!! #
# ------------------------------------ #

my_qos = 2

def on_connect(mqttc, obj, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    #print("MsgId: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


mqttc = mqtt.Client("panel-publisher")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()


# Simulazione dell'invio di 20 misurazioni di 20 pannelli.
# Viene inviato un dato float "grezzo", che si ritiene sia
# preciso fino alla terza cifra decimale; dalla quarta in poi
# verrà arrotondato dal subscriber.
# Esempio: Viene inviato il dato grezzo 115.72652869419638.
# La misurazione è accurata fino alla terza cifra decimale,
# quindi è considerato attendibile 115.726; la quarta cifra
# viene approssimata dal subscriber, che quindi utilizzerà come
# dato per i passaggi successivi 115.7265.
try:
    while True:
        for i in range(1, 21):
            topic = "telemetry/panel/p"+str(i)
            power = random.uniform(0, 200)
            pkd_power = struct.pack('f', power)
            (rc, mid) = mqttc.publish(topic, pkd_power, qos=my_qos)
            print("Pub on '"+topic+"': "+str(power)+" "+str(mid)+" Rc: "+str(rc)+" @"+str(time.time()))
        print("\n-------------------------\n")
        time.sleep(5)
except KeyboardInterrupt:
    mqttc.disconnect()
    print("Exiting...")
    sys.exit()