# publish_command.py
import sys
import paho.mqtt.publish as publish

if len(sys.argv) < 3:
    print("Usage: python publish_command.py <topic> <message>")
    sys.exit(1)

topic = sys.argv[1]
message = sys.argv[2]

# Publish to local broker
publish.single(topic, message, hostname="172.20.10.2", port=1883)
print(f"Published '{message}' to topic '{topic}'")
