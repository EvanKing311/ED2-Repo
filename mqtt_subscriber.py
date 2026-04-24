#MQTT subscriber for Matlab Messages
import os
import sys

#Set up Django environment
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EGNSite.settings')

#start django
import django
django.setup()

#MQTT and Message import
import paho.mqtt.client as mqtt
from MatlabApp.models import Message

#Channel layer for WebSocket push
import json
import re
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

#setup MQTT
BROKER = "sciencelabtoyou.com"
PORT = 1885
TOPIC = "raspi/to_django"
allow_anonymous = True

#when client connects
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {BROKER}:{PORT}")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: '{TOPIC}'")
        print(f"Waiting for messages from MATLAB...\n")
    else:
        print(f"Connection failed with code {rc}")


def parse_payload(message_text):
    # First attempt — standard JSON
    try:
        return json.loads(message_text)
    except json.JSONDecodeError:
        pass

    # Second attempt — fix unquoted keys by replacing word: with "word":
    try:
        fixed = re.sub(r'(\{|,)\s*(\w+)\s*:', r'\1"\2":', message_text)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return {'raw': message_text}


#when message received
def on_message(client, userdata, msg):
    from django.db import connection
    
    message_text = msg.payload.decode()
    print(f"\n Received: '{message_text}' on topic '{msg.topic}'")

    connection.close()  # forces Django to open a fresh connection

    MAX_MESSAGES = 5000

    try:
        # Save to Message model (mySQL)
        Message.objects.create(message=message_text)

        # Keep only the most recent MAX_MESSAGES readings
        count = Message.objects.count()
        if count > MAX_MESSAGES:
            # Delete oldest entries beyond the cap
            oldest_ids = Message.objects.order_by('timestamp').values_list('id', flat=True)[:count - MAX_MESSAGES]
            Message.objects.filter(id__in=list(oldest_ids)).delete()

        print(f" Saved to Message table (total messages: {min(count, MAX_MESSAGES)})")
    except Exception as e:
        print(f" Error saving to database: {e}")

    # Push to WebSocket
    try:
        payload = parse_payload(message_text)

        async_to_sync(channel_layer.group_send)(
            'sensor_data',
            {
                'type': 'sensor_update',
                'data': payload
            }
        )
        print(f" Pushed to WebSocket group 'sensor_data'")
    except Exception as e:
        print(f" Error pushing to WebSocket: {e}")


def main():
    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(" Starting MQTT Subscriber...")
        
        client.connect(BROKER, PORT, 60)
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n Subscriber stopped by user")
        client.disconnect()

    except Exception as e:
        print(f"\n Error: {e}")


if __name__ == "__main__":
    main()