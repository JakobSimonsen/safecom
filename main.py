import paho.mqtt.client as mqtt
from mqtt_client import MQTT_Client
from .recorder import Recorder

#setting public broker
broker, port = 'mqtt.item.ntnu.no', 1883

client = MQTT_Client()
client.start(broker, port)

recording = Recorder()
