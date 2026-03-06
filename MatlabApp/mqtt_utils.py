import paho.mqtt.publish as publish
import json

BROKER_HOST = "172.20.10.2"
BROKER_PORT = 1883
TOPIC = "django/to_raspi"
allow_anoynmous = True

def send_command(payload, user):
    """
    Send payload to Raspberry Pi.
    Accepts either a string command OR full JSON dict.
    """

    # If payload is just a string, wrap it
    if isinstance(payload, str):
        payload = {
            "command": payload
        }

    # Attach user info
    payload["user_id"] = user.id
    payload["username"] = user.username

    try:
        publish.single(
            TOPIC,
            payload=json.dumps(payload),
            hostname=BROKER_HOST,
            port=BROKER_PORT
        )

        print("Published to MQTT:")
        print(json.dumps(payload, indent=4))

        return True

    except Exception as e:
        print(f"Failed to publish command: {e}")
        return False