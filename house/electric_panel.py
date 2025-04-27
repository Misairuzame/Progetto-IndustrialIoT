import random
import struct
import sys
import time
import uuid

import paho.mqtt.client as mqtt

import my_functions
import time_scaling
import unit_conversion

time_scale = time_scaling.get_time_scale()

topic_internal1 = "internal/tofeed"
topic_internal2 = "internal/getfrombatteries"
topic_internal3 = "internal/getfromgrid"

get_from_grid = 0
feed_into_grid = 0

my_qos = 2


def on_connect(mqttc, obj, flags, rc):
    global topic_internal1, topic_internal2, topic_internal3
    mqttc.subscribe(topic_internal1, qos=my_qos)
    mqttc.subscribe(topic_internal2, qos=my_qos)
    mqttc.subscribe(topic_internal3, qos=my_qos)


def on_message(mqttc, obj, msg):
    global get_from_grid, feed_into_grid
    if msg.topic == topic_internal3:
        get_from_grid = struct.unpack("f", msg.payload)[0]
    elif msg.topic == topic_internal1:
        feed_into_grid = struct.unpack("f", msg.payload)[0]


if __name__ == "__main__":
    port = 1883
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    mqtt_name = "pub-elpan-"
    mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_name)]
    mqttc = mqtt.Client(client_id=mqtt_name + mqtt_rand_id)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect("localhost", port, 60)
    mqttc.loop_start()

    try:
        while True:
            now = time_scaling.get_scaled_time()
            consumption_required = unit_conversion.watt_instant_to_watth(
                random.uniform(0.75, 1.25)
                * my_functions.consumption_function(now)
                * (2250 / 1.72)
            )

            # Simulazione: il quadro elettrico "chiede" energia alle batterie, se è possibile le batterie
            # gliela forniscono tutta, sennò (per semplicità) non gliene forniscono alcuna e tutta la
            # corrente viene presa dalla rete elettrica.
            mqttc.publish(
                topic_internal2, struct.pack("f", consumption_required), qos=my_qos
            )
            time.sleep(1)

            topic1 = "telemetry/electricpanel/consumption-grid"
            pkd_consumption = struct.pack("f", get_from_grid)
            (rc, mid) = mqttc.publish(topic1, pkd_consumption, qos=my_qos)
            print(
                str(time.time())
                + "\tPub on '"
                + topic1
                + "': "
                + str(get_from_grid)
                + " "
                + str(mid)
                + " Rc: "
                + str(rc)
            )

            topic2 = "telemetry/electricpanel/feeding"
            pkd_feed = struct.pack("f", feed_into_grid)
            (rc, mid) = mqttc.publish(topic2, pkd_feed, qos=my_qos)
            print(
                str(time.time())
                + "\tPub on '"
                + topic2
                + "': "
                + str(feed_into_grid)
                + " "
                + str(mid)
                + " Rc: "
                + str(rc)
            )

            topic3 = "telemetry/electricpanel/consumption-required"
            pkd_consumption_req = struct.pack("f", consumption_required)
            (rc, mid) = mqttc.publish(topic3, pkd_consumption_req, qos=my_qos)
            print(
                str(time.time())
                + "\tPub on '"
                + topic3
                + "': "
                + str(consumption_required)
                + " "
                + str(mid)
                + " Rc: "
                + str(rc)
            )

            time.sleep(4)
    except KeyboardInterrupt:
        mqttc.disconnect()
        time.sleep(1)
        print("Electric panel exiting...")
        sys.exit()
