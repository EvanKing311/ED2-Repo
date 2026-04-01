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

#when message received
def on_message(client, userdata, msg):
    message_text = msg.payload.decode()
    print(f"\n Received: '{message_text}' on topic '{msg.topic}'")
    
    try:
        #save to Message model (mySQL)
        Message.objects.create(message=message_text)
        message_count = Message.objects.count()
        print(f" Saved to Message table (total messages: {message_count})")
    except Exception as e:
        print(f" Error saving to database: {e}")


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