import paho.mqtt.client as mqtt
import sys
import struct
import random
import time
import uuid
import my_functions
import time_scaling
import unit_conversion

time_scale = time_scaling.get_time_scale()

topic_internal1 = "internal/tofeed"
topic_internal2 = "internal/getfrombatteries"
topic_internal3 = "internal/getfromgrid"

get_from_grid = 0
feed_into_grid = 0

max_charge = 5 # Unità di misura: kWh
# 1kWh = 1kW * 1h = 1kW * 3600s
# Visto che le misurazioni vengono
# inviate ogni 5 secondi, e sono in kW (sarebbe kW per 5 secondi),
# allora possiamo definire la carica massima
# come max_charge*kWh / (5s/3600s)
# Così otteniamo un valore in "kW" (per 5 secondi)

max_charge_kw = max_charge/(5/3600)
charge = 0

produced_now = 0

my_qos = 2

def on_connect_cc(mqttclient, obj, flags, rc):
    #print("Connected with result code: " + str(rc))
    #global mqttc, topic_internal1, topic_internal2, topic_internal3, topic_internal4
    #mqttc.subscribe(topic_internal1, qos=my_qos)
    #mqttc.subscribe(topic_internal2, qos=my_qos)
    #mqttc.subscribe(topic_internal3, qos=my_qos)
    #mqttc.subscribe(topic_internal4, qos=my_qos)
    pass


def on_message_cc(mqttclient, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    #global feed_into_grid, get_from_grid, produced_now
    #if msg.topic == topic_internal1:
        #produced_now = struct.unpack('f', msg.payload)
        #feed_into_grid = charge_batteries(produced_now)
        #if feed_into_grid > 0:
            #mqttc.publish(topic_internal2, struct.pack('f', float(feed_into_grid)), qos=my_qos)
            #feed_into_grid = feed_into_grid
    #elif msg.topic == topic_internal3:
        #to_give = struct.unpack('f', msg.payload)
        #get_from_grid = give_charge(to_give)
        #if get_from_grid > 0:
            #mqttc.publish(topic_internal4, struct.pack('f', float(get_from_grid)), qos=my_qos)
            #pass
    pass


def on_connect_ep(mqttc, obj, flags, rc):
    #print("Connected with result code: " + str(rc))
    global topic_internal1, topic_internal2, topic_internal3
    mqttc.subscribe(topic_internal1, qos=my_qos)
    mqttc.subscribe(topic_internal2, qos=my_qos)
    mqttc.subscribe(topic_internal3, qos=my_qos)
    #mqttc.subscribe(topic_internal4, qos=my_qos)
    pass


def on_message_ep(mqttc, obj, msg):
    global get_from_grid, feed_into_grid
    if msg.topic == topic_internal3:
        get_from_grid = struct.unpack('f', msg.payload)[0]
        #print("Get from grid: "+str(get_from_grid))
    elif msg.topic == topic_internal1:
        feed_into_grid = struct.unpack('f', msg.payload)[0]
        #print("Feed into grid: "+str(feed_into_grid))


if __name__ == '__main__':
    port = 1883
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    mqtt_elpan_name = "pub-elpan-"
    mqtt_elpan_rand_id = str(uuid.uuid4())[:23-len(mqtt_elpan_name)]
    mqttc_elpan = mqtt.Client(client_id=mqtt_elpan_name+mqtt_elpan_rand_id)
    mqttc_elpan.on_connect = on_connect_ep
    mqttc_elpan.on_message = on_message_ep
    
    mqttc_elpan.connect("localhost", port, 60)
    mqttc_elpan.loop_start()

    # mqtt_charcont_name = "pub-charcontr-"
    # mqtt_charcont_rand_id = str(uuid.uuid4())[:23-len(mqtt_charcont_name)]
    # mqttc_charcont = mqtt.Client(client_id=mqtt_charcont_name+mqtt_charcont_rand_id)
    # mqttc_charcont.on_message = on_message_cc
    # mqttc_charcont.on_connect = on_connect_cc
    
    # mqttc_charcont.connect("localhost", port, 60)
    # mqttc_charcont.loop_start()

    try:
        while True:
            now = time_scaling.get_scaled_time()
            consumption_required = unit_conversion.watt_instant_to_watth(random.uniform(0.75, 1.25)*my_functions.consumption_function(now)*(2250/1.72))
            #print("House consumption: "+str(consumption_required))

            # Simulazione: il quadro elettrico "chiede" energia alle batterie, se è possibile le batterie
            # gliela forniscono tutta, sennò (per semplicità) non gliene forniscono alcuna e tutta la
            # corrente viene presa dalla rete elettrica.
            #get_from_grid = give_charge(consumption_required)
            mqttc_elpan.publish(topic_internal2, struct.pack('f', consumption_required), qos=my_qos)
            time.sleep(1)

            topic1 = "telemetry/electricpanel/consumption-grid"
            pkd_consumption = struct.pack('f', get_from_grid)
            (rc, mid) = mqttc_elpan.publish(topic1, pkd_consumption, qos=my_qos)
            print(str(time.time())+"\tPub on '"+topic1+"': "+str(get_from_grid)+" "+str(mid)+" Rc: "+str(rc))

            topic2 = "telemetry/electricpanel/feeding"
            pkd_feed = struct.pack('f', feed_into_grid)
            (rc, mid) = mqttc_elpan.publish(topic2, pkd_feed, qos=my_qos)
            print(str(time.time())+"\tPub on '"+topic2+"': "+str(feed_into_grid)+" "+str(mid)+" Rc: "+str(rc))

            topic3 = "telemetry/electricpanel/consumption-required"
            pkd_consumption_req = struct.pack('f', consumption_required)
            (rc, mid) = mqttc_elpan.publish(topic3, pkd_consumption_req, qos=my_qos)
            print(str(time.time())+"\tPub on '"+topic3+"': "+str(consumption_required)+" "+str(mid)+" Rc: "+str(rc))

            time.sleep(4)
    except KeyboardInterrupt:
        mqttc_elpan.disconnect()
        time.sleep(1)
        print("Electric panel exiting...")        
        sys.exit()

# topic = "telemetry/chargecontroller/c1"
# pkd_charge = struct.pack('f', charge)
# (rc, mid) = mqttc.publish(topic, pkd_charge, qos=my_qos)
# print(str(time.time())+"\tPub on '"+topic+"': "+str(charge)+" "+str(mid)+" Rc: "+str(rc))