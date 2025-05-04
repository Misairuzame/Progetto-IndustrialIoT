import struct
import sys
import time
import uuid

import paho.mqtt.client as mqtt

topic1_name = "telemetry/panel/#"
topic2_name = "telemetry/chargecontroller/#"
topic3_name = "telemetry/electricpanel/#"
topic_internal1 = "internal/totalpanels"

my_qos = 2


def on_connect(client, userdata, flags, rc, properties):
    # client.subscribe(topic1_name, qos=my_qos)
    # client.subscribe(topic2_name, qos=my_qos)
    # client.subscribe(topic3_name, qos=my_qos)
    client.subscribe("#", qos=my_qos)


def on_message(client, userdata, msg):
    global current_panels, current_batteries, current_elmeter
    unpacked = struct.unpack("f", msg.payload)[0]
    print(f"Received: {msg.topic}: {unpacked}")


port = 1883
if len(sys.argv) > 1:
    port = int(sys.argv[1])

mqtt_client_name = "sub-contatore-"
mqtt_rand_id = str(uuid.uuid4())[: 23 - len(mqtt_client_name)]
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=mqtt_client_name + mqtt_rand_id,
    clean_session=False,
)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", port, 60)


if __name__ == "__main__":
    try:
        client.loop_start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
        print("Subscriber read all exiting...")
        sys.exit()
