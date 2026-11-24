"""Simulator ESP32: publish data sensor & menerima perintah kontrol/alert via MQTT.
Butuh paho-mqtt >= 2.0  (pip install -r requirements.txt)
"""
import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
TOPIC_ALERT = "iot/alert"

lampu = "OFF"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Terhubung ke broker (kode: {reason_code})")
    client.subscribe([(TOPIC_KONTROL, 0), (TOPIC_ALERT, 0)])


def on_message(client, userdata, msg):
    global lampu
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        print(f"← {msg.topic}: {msg.payload!r}")
        return
    if msg.topic == TOPIC_KONTROL:
        lampu = str(data.get("action", "")).upper() or lampu
        print(f"← KONTROL diterima: {data}  => lampu {lampu}")
    elif msg.topic == TOPIC_ALERT:
        print(f"← ALERT: {data.get('message')}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()

print("ESP32 Simulator berjalan... Ctrl+C untuk stop")
try:
    while True:
        data = {
            "suhu": round(random.uniform(25, 32), 1),
            "kelembaban": round(random.uniform(55, 80), 1),
            "timestamp": datetime.now().isoformat(),
        }
        client.publish(TOPIC_SENSOR, json.dumps(data))
        print(f"→ Publish: {data}")
        time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
