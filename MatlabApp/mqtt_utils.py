import paho.mqtt.publish as publish
import json

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1885
TOPIC = "pendulum/cmd"
allow_anoynmous = True

def send_command(payload):
#Send payload as either JSON or plain string to MQTT broker depending on the command

    # If payload is just a string, wrap it
    if isinstance(payload, str):
        payload = {
            "command": payload
        }

    # Attach user info (COMMENTED OUT, NO USER AUTH ON PI SIDE)
    #payload["user_id"] = user.id
    #payload["username"] = user.username

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