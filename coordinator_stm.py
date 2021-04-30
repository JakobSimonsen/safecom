import time
import re
from mqtt_client import MQTT_Client
from Audio import recorder, playback
from stmpy import Driver, Machine
from threading import Thread
import collections
import queue
from playsound import playsound


class Coordinator:
    def __init__(self):
        self.channel = "team2/channel1"#None #Bytt ut med å bruke channels.json-objektet
        self.priority = 0
        self.client = None
        self.high_priority_queue = []
        self.low_priority_queue = []
        self.times_retried = 0

        # self.voice_msg??

    def start_recording(self):
        print("start_recording called in coordinator")
        #self.recorder.record()
        self.stm_driver.send("start", "recorder_stm")

    def end_recording(self, priority):
        print("ending recording")
        self.priority = 1 if priority else 0
        # self.recorder.stop()
        # self.recorder.process()
        self.stm_driver.send("stop", "recorder_stm")

    def play_msg(self, filename):
        print("playing message w. "+filename)
        regex_priority = "^(priority_1)"
        z = re.findall(regex_priority, filename)
        if(z):
            self.high_priority_queue.append(filename)
        else:
            self.low_priority_queue.append(filename)

        if(len(self.high_priority_queue)> 0):
            for i in self.high_priority_queue:
                playsound(self.high_priority_queue.pop(0))
        elif(len(self.low_priority_queue)>0):
            for i in self.low_priority_queue:
                playsound(self.low_priority_queue.pop(0))

        self.stm_driver.send("done_playing", "coordinator")
        #self.stm_driver.send("start", "playback_stm", [filename])

        #self.stm_driver.send("done", "playback_stm")

    def send_msg(self, fileName):
        self.client.publish_recorded_message(self.channel, self.priority, fileName)

    def set_new_channel(self, new_channel):
        print("setting new channel")
        if (self.channel != None):
            self.client.client.unsubscribe(self.channel)
        self.channel = new_channel
        self.client.client.subscribe(new_channel)
        print("subscribed to", new_channel)

    def in_sending_state(self):
        print("Now in sending state")

    """
    def add_to_queue(self, msg_reference):
        try:
        # High priority: 1
        if msg_reference[1] == 1:
            self.high_priority_queue.put(msg_reference) #[filename, priority, topic]
        except:
            print("error adding to high priority queue")
        # Low priority: 0
        if msg_reference[1] == 0:
            self.low_priority_queue.put(msg_reference) #[filename, priority, topic]
        except:
            print("error adding to low priority queue")
    """
    def resend_message(self, filename_in_list):
        time.sleep(0.5)
        self.times_retried += 1
        if self.times_retried > 100:
            self.stm_driver.send('sending_success', 'coordinator')

        self.send_msg(filename_in_list[0])




coordinator = Coordinator()
t0 = {'source': 'initial',
      'target': 'idle'}

t1 = {'trigger': 'record_button',
      'source': 'idle',
      'target': 'recording'}

t2 = {'trigger': 'new_incoming_msg',
      'source': 'idle',
      'target': 'playing'}

t3 = {'trigger': 'play_from_history',
      'source': 'idle',
      'target': 'playing'}

t4 = {'trigger': 't3',
      'source': 'recording',
      'target': 'saving_file'}

t5 = {'trigger': 'end_recording_button',
      'source': 'recording',
      'target': 'saving_file',
      'effect': 'end_recording(*)'}

t6 = {'trigger': 'file_saved',
      'source': 'saving_file',
      'effect': 'send_msg(*)',
      'target': 'sending'}

t7 = {'trigger': 't1',
      'source': 'playing',
      'target': 'idle'}

t9 = {'trigger': 'sending_failed',
      'source': 'sending',
      'target': 'saving_file'}

t10 = {'trigger': 'sending_success',
       'source': 'sending',
       'target': 'idle'}

t11 = {'trigger': 'play_incoming_message',
        'source': 'idle',
        'effect': 'play_msg(*)',
        'target': 'playing'}

t12 = {'trigger': 'done_playing',
        'source': 'playing',
        'target': 'idle'}

idle = {'name': 'idle', 'change_channel': 'set_new_channel(*)'}

recording = {'name': 'recording',
             'entry': 'start_recording; start_timer("t3", 180000); ',
             'play_incoming_msg': 'defer'}

saving_file = {'name': 'saving_file',
                'play_incoming_msg': 'defer'}

sending = {'name': 'sending',
           'entry': 'in_sending_state', #'send_msg',
           'play_incoming_msg': 'defer',
           'sending_failed': 'add_to_top_of_queue(*)'}

playing = {'name': 'playing',
           'play_incoming_msg': 'defer'}

machine = Machine(name='coordinator', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t9, t10, t11, t12], obj=coordinator, states=[
                  idle, recording, saving_file, playing, sending])
coordinator.stm = machine

driver = Driver()
driver.add_machine(machine)

recorderInstance = recorder.Recorder(driver)
playbackInstance = playback.Player(driver)
client = MQTT_Client(driver)
coordinator.client = client
coordinator.client.stm_driver = driver
client.start('mqtt.item.ntnu.no', 1883)

driver.add_machine(recorderInstance.stm)
driver.add_machine(playbackInstance.playback_stm)
driver.start()
coordinator.stm_driver = driver
#playback.player.stm_driver = driver

#Just used to test the coordination between recorder.py, mqtt_client.py and coordinator atm -Toni
'''
driver.send("record_button", "coordinator")
coordinator.channel = "team2"
time.sleep(3)
print("Sending end_recording_button trigger")
driver.send("end_recording_button", "coordinator")
'''








# Just used to test the recorder.py atm -Toni
#driver.send("start", "recorder_stm")
# time.sleep(3)
#driver.send("stop", "recorder_stm")
