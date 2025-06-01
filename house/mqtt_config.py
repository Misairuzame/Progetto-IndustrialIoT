import struct
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import paho.mqtt.client as mqttc

mqtt_address = "localhost"
mqtt_port = 1883

topic_internal_totalpanels = "internal/totalpanels"
topic_internal_tofeed = "internal/tofeed"
topic_internal_getfrombatteries = "internal/getfrombatteries"
topic_internal_chargebatteries = "internal/chargebatteries"
topic_internal_getfromgrid = "internal/getfromgrid"

topic_charge = "telemetry/chargecontroller/c1"

topic_elpanel_base = "telemetry/electricpanel/"
topic_consumption_grid = "telemetry/electricpanel/consumption-grid"
topic_feeding = "telemetry/electricpanel/feeding"
topic_consumption_required = "telemetry/electricpanel/consumption-required"

topic_panel_base = "telemetry/panel/"
topic_panel_prefix = "telemetry/panel/p"  # .../p1, .../p2, .../p3, etc.

topic_panels_wildcard = "telemetry/panel/#"

mqtt_qos = 2


def pack_and_publish(mqttc: "mqttc.Client", topic: str, payload: float):
    pkd_payload = struct.pack("f", payload)
    return mqttc.publish(topic, pkd_payload, qos=mqtt_qos)


def generate_client_name(prefix: str):
    mqtt_rand_id = str(uuid.uuid4())[: 23 - len(prefix)]
    return prefix + "-" + mqtt_rand_id
