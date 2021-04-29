import time

from mqtt_client import MQTT_Client
from Audio import recorder, playback
from stmpy import Driver, Machine
from threading import Thread
import collections
import queue

class Coordinator:
    def __init__(self):
        self.channel = None
        self.priority = 0
        self.client = None
        self.high_priority_queue = queue.Queue()
        self.low_priority_queue = queue.Queue()
        self.times_retried = 0

        #self.voice_msg??

    def start_recording(self):
        print("starting recording")
        #self.recorder.record()
        self.stm_driver.send("start", "recorder_stm")

    def end_recording(self):
        print("ending recording")
        #self.recorder.stop()
        #self.recorder.process()
        self.stm_driver.send("stop", "recorder_stm")

    def play_msg(self):
        print("playing message")
        #self.player.play()
        #??
        self.stm_driver.send("start", "playback_stm")
        self.stm_driver.send("done", "playback_stm")

    def send_msg(self, filename):
        print("sending message")
        self.client.publish_recorded_message(self.channel, self.priority, filename)


    def set_new_channel(self, new_channel):
        print("setting new channel")
        self.channel = new_channel
        self.client.subscribe(new_channel)
        print("subscribed to", new_channel)
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

t1 = {'trigger':'record_button',
      'source': 'idle',
      'target': 'recording'}

t2 = {'trigger':'new_incoming_msg',
      'source': 'idle',
      'target': 'playing'}

t3 = {'trigger':'play_from_history',
      'source': 'idle',
      'target': 'playing'}

t4 = {'trigger':'t3',
      'source': 'recording',
      'target': 'saving_file'}

t5 = {'trigger':'end_recording_button',
      'source': 'recording',
      'target': 'saving_file'}

t6 = {'trigger':'file_saved',
      'source': 'saving_file',
      'target': 'sending'}

t7 = {'trigger':'t1',
      'source': 'playing',
      'target': 'idle'}

t8 = {'trigger':'stop_button',
      'source': 'playing',
      'target': 'idle'}

t9 = {'trigger':'sending_failed',
      'source': 'sending',
      'target': 'saving_file'}

t10 = {'trigger':'sending_success',
      'source': 'sending',
      'target': 'idle'}
t11 = {'trigger':'fileSaved',
      'source': 'saving_file',
      'target': 'sending'}


idle = {'name': 'idle', 'change_channel': 'set_new_channel(*)'}

recording = {'name': 'recording',
             'entry': 'start_recording; start_timer("t3", 180000); ',
             'exit': 'end_recording',
             'new_incoming_msg': 'defer'}

saving_file = {'name': 'saving_file',
                 'new_incoming_msg': 'defer'}

sending = {'name': 'sending',
           'entry': 'send_msg(*)',
           'new_incoming_msg': 'defer'
           'sending_failed': 'resend_message(*)'
           }

playing = {'name': 'playing',
           'entry': 'start_timer("t1", 10000); play_msg',
           'new_incoming_msg': 'defer'}

machine = Machine(name='coordinator', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11], obj=coordinator, states=[idle, recording, saving_file, playing, sending])
coordinator.stm = machine

driver = Driver()
driver.add_machine(machine)
coordinator.client.stm_driver = driver

recorderInstance = recorder.Recorder(driver)
client = MQTT_Client(driver)
coordinator.client = client
client.start('mqtt.item.ntnu.no', 1883)

driver.add_machine(recorderInstance.stm)
driver.add_machine(playback.playback_stm)
driver.start()
coordinator.stm_driver = driver
playback.player.stm_driver = driver

#Just used to test the recorder.py atm -Toni
driver.send("start", "recorder_stm")
time.sleep(3)
driver.send("stop", "recorder_stm")









