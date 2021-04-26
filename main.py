import paho.mqtt.client as mqtt
from mqtt_client import MQTT_Client
import time
#from recorder import Recorder

#setting public broker
broker, port = 'mqtt.item.ntnu.no', 1883

client = MQTT_Client()
client.start(broker, port)

sub_client = MQTT_Client()
sub_client.start(broker, port)

#time.sleep(10)

client.publish_recorded_message("/audio_test_2", 3, "wav_files/test_sound.wav")


#recorder = Recorder()
