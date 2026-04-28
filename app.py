from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import json
import threading
import time

app = Flask(__name__)

# =========================================================
# CONFIG
# =========================================================

LOCATION_MAP = {
    "LIBRARY": "library",
    "CAFE": "cafe",
    "CLUB": "club",
}

INACTIVE_TIMEOUT = 5  # seconds before a device is considered "offline"

def normalize_location(location_id):
    return str(location_id).strip().upper() if location_id else "UNKNOWN"

# =========================================================
# STATE STORAGE
# =========================================================
latest_readings = {}

# =========================================================
# CLASSIFIER
# =========================================================
def classify_environment_and_vibe(noise, location_id):
    location_id = normalize_location(location_id)

    environment = LOCATION_MAP.get(location_id, "unknown")

    if noise < 37:
        vibe = "Calm / Focused 📚"
    elif noise < 56:
        vibe = "Moderate / Social ☕"
    else:
        vibe = "Loud / Energetic 🔥"

    return environment, vibe

# =========================================================
# MQTT
# =========================================================
BROKER_IP = "your-broker-ip"
BROKER_PORT = 1883
TOPIC = "env/raw/#"

def on_connect(client, userdata, flags, rc):
    print("MQTT connected")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        noise = payload.get("noise_level_db")
        temp = payload.get("temperature_f")
        location_id = payload.get("location_id")
        device_id = payload.get("device_id")

        if noise is None or location_id is None:
            return

        noise = float(noise)
        now = time.time()

        env, vibe = classify_environment_and_vibe(noise, location_id)

        key = normalize_location(location_id)

        latest_readings[key] = {
            "device_id": device_id,
            "location_id": key,
            "environment": env,
            "vibe_label": vibe,
            "noise_level_db": round(noise, 2),
            "temperature_f": round(temp, 2) if temp is not None else None,
            "timestamp": now
        }

    except Exception as e:
        print("MQTT error:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_IP, BROKER_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print("MQTT connection failed:", e)

threading.Thread(target=start_mqtt, daemon=True).start()

# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live")
def live():
    now = time.time()

    response = {}

    # Always show BOTH tiles (even if missing)
    for loc in ["LIBRARY", "CAFE", "CLUB"]:
        loc_key = loc
        data = latest_readings.get(loc_key)

        if data:
            last_seen = data.get("timestamp", 0)
            active = (now - last_seen) <= INACTIVE_TIMEOUT

            response[loc_key] = {
                **data,
                "active": active,
                "last_seen_ago": round(now - last_seen, 1)
            }
        else:
            response[loc_key] = {
                "location_id": loc_key,
                "environment": loc.lower(),
                "vibe_label": "No Data",
                "noise_level_db": None,
                "temperature_f": None,
                "timestamp": None,
                "active": False,
                "last_seen_ago": None
            }

    return jsonify(response)

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)