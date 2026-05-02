import sys
import paho.mqtt.client as mqtt

#2nd and 3rd arguments are topic and message (1st is script name)
topic = sys.argv[1]
message = sys.argv[2]

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish(topic, message)
client.disconnect()
