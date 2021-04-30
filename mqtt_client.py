from threading import Thread
import os
import paho.mqtt.client as mqtt
import json as js
import base64
import uuid
import time
from playsound import playsound


class MQTT_Client:
    def __init__(self, driver):
        self.broker = None
        self.port = None
        self.driver = driver
        self.client_id = str(uuid.uuid1())  # Creates a client ID
        self.history = []
        self.is_blackbox = False
        self.channel = None
        self.firstTimeRunning = True

    def on_connect(self, client, userdata, flags, rc):
        print('on_connect(): {}'.format(mqtt.connack_string(rc)))
        if (self.firstTimeRunning):
            self.firstTimeRunning = False
        else:
            print("Subsribed to "+self.channel)
            self.client.subscribe(self.channel)

    def on_message(self, client, userdata, msg):
        #print('on_message(): topic: {}'.format(msg.topic))
        #
        # data['seq_number'] --> int
        # data['call_id'] --> str
        # data['priority'] --> int
        # data['data'] - decode with b64decode
        # data['last_packet] --> bool

        # Decode payload into json string
        decoded_string = msg.payload.decode('utf-8')
        js_str = js.loads(decoded_string)

        # Decode audio
        json_data = js_str['data']
        byte_array = base64.b64decode(json_data)

        try:
            # If new call - create new audio file
            if js_str['client_id'] != self.client_id:
                
                #priority_1_filename.wav
                file_name = f"output_audio_files/priority_{js_str['priority']}_{js_str['call_id']}-output.wav"
                if js_str['seq_number'] == 0:
                    output_file = open(file_name, "wb")
                    output_file.write(byte_array)
                    output_file.close()

                # play correct audio file
                elif js_str['last_packet'] == True:

                    # if blackbox append to history no matter what
                    if self.is_blackbox:
                        self.history.append((file_name))

                    # checking if history is larger then 5
                    elif(len(self.history) < 5):
                        self.history.append(file_name)
                    # if history is more then 5 remove first element and add new to history
                    else:
                        os.remove(self.history.pop(0))
                        self.history.append(file_name)
                        print(self.history)

                    self.driver.send("play_incoming_message",
                                     'coordinator', [file_name])

                # Append to correct audio file
                else:
                    output_file = open(file_name, "ab")
                    output_file.write(byte_array)
                    output_file.close()

        except Exception as e:
            print("Exception" + str(e))

    def get_set_broker(self, broker=None):
        if broker:
            self.broker = broker
        return self.broker

    def get_set_port(self, port=None):
        if port:
            self.port = port
        return self.port

    def start(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # setting broker and port (self.variables)
        self.broker = broker
        self.port = port
        print('Connecting to {}:{}'.format(broker, port))
        self.client.connect(broker, port)

        # self.client.subscribe(subscribe_channel)

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()

        except KeyboardInterrupt:
            pass
            # print('Interrupted')
            # self.client.disconnect()

    def publish_recorded_message(self, topic, priority, filename):

        # Turn audio file into bytestream
        audio_file = open(filename, 'rb')
        audio_string = audio_file.read()
        audio_file.close()
        byte_array = bytearray(audio_string)
        encoded_string = base64.b64encode(byte_array)

        time.sleep(1)

        # establishes connection
        #client_connect = self.client.connect(self.broker, self.port)

        # add bytestream to the data json object
        all_data = list(encoded_string.decode('ascii'))

        # Chunk size of data
        seq_number = 0
        chunk_size = 5000

        # Splits data into smaller chunks
        all_data = [all_data[i:i + chunk_size]
                    for i in range(0, len(all_data), chunk_size)]
        last_sequene_number = len(all_data)-1

        # unique ID for the whole call/audio-file
        call_id = str(uuid.uuid1())
        for i, data_chunk in enumerate(all_data):
            # Current data packet
            data_packet = {}
            # Adds client ID to all packets
            data_packet['client_id'] = self.client_id
            data_packet['call_id'] = call_id
            data_packet['seq_number'] = i
            data_packet['priority'] = priority
            data_packet['last_packet'] = (i == last_sequene_number)

            data_packet['data'] = "".join(data_chunk)
            send_data = js.dumps(data_packet)

            # publish(topic, payload=None, qos=0, retain=False) - default values
            result = self.client.publish(
                topic=topic, payload=send_data, qos=2, retain=False)

            # If one of the packets don't work
            if result[0] > 0:
                # send to state machine that the message failed
                self.driver.send('sending_failed', 'coordinator', [filename])
                break
        else:
            self.driver.send('sending_success', 'coordinator')

    def GetHistory(self):
        return self.history
