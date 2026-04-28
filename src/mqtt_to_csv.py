import paho.mqtt.client as mqtt
import json
import csv
import os
from datetime import datetime

BROKER_IP = "your-broker-ip" # Replace with local MQTT broker IP when running locally
BROKER_PORT = 1883
TOPIC = "env/raw/#"
CSV_FILE = "vibe_data.csv"

file_exists = os.path.isfile(CSV_FILE)

with open(CSV_FILE, mode="a", newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow([
            "timestamp_received",
            "device_id",
            "ip",
            "location_id",
            "session_id",
            "timestamp_device",
            "temperature_f",
            "noise_level_db"
        ])

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # skip incomplete rows
        if payload.get("temperature_f") is None or payload.get("noise_level_db") is None:
            return

        row = [
            datetime.utcnow().isoformat(),
            payload.get("device_id"),
            payload.get("ip"),
            payload.get("location_id"),
            payload.get("session_id"),
            payload.get("timestamp"),
            payload.get("temperature_f"),
            payload.get("noise_level_db")
        ]

        print(row)

        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)

    except Exception as e:
        print("Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKER_PORT, 60)
client.loop_forever()
