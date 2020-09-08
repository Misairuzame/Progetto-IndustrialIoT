import paho.mqtt.client as mqtt
import sys
import struct
import random
import time
import uuid
import time_scaling
import my_functions
import meteo_info
import unit_conversion

time_scale = time_scaling.get_time_scale()
my_qos = 2

def on_connect(mqttc, obj, flags, rc):
    #print("Connected with result code: " + str(rc))
    pass


def on_message(mqttc, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    pass


def on_publish(mqttc, obj, mid):
    #print("MsgId: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    #print("Subscribed: " + str(mid) + " " + str(granted_qos))
    pass


def my_main(arg1):
    port = 1883
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    mqtt_client_name = "pub-panel"+arg1+"-"
    mqtt_rand_id = str(uuid.uuid4())[:23-len(mqtt_client_name)]
    mqttc = mqtt.Client(client_id=mqtt_client_name+mqtt_rand_id)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.connect("localhost", port, 60)
    mqttc.loop_start()

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
            topic = "telemetry/panel/p"+str(arg1)
            now = time_scaling.get_scaled_time()
            # Se meteo_info.get_meteo...() fornisce quanta percentuale di
            # nuvole ci sono, (100-meteo_info...) può significare, in prima approssimazione,
            # "quanto sole c'è", e quindi, quanto può produrre un pannello solare.
            # Inoltre si moltiplica per un valore casuale per rendere i dati un po' più
            # differenziati fra loro. L'ultimo valore (250/4.5) fa sì che la produzione massima
            # istantanea del singolo pannello solare sia circa 250 W.
            power = unit_conversion.watt_instant_to_watth(random.uniform(0.8, 1)*((100-meteo_info.get_meteo_internal())/100)*my_functions.solar_power_function(now)*(250/4.5))
            pkd_power = struct.pack('f', power)
            (rc, mid) = mqttc.publish(topic, pkd_power, qos=my_qos)
            print(str(time.time())+"\tPub on '"+topic+"': "+str(power)+" "+str(mid)+" Rc: "+str(rc))
            time.sleep(5)
    except KeyboardInterrupt:
        mqttc.disconnect()
        time.sleep(1)
        print("Panel "+arg1+" exiting...")
        sys.exit()