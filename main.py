import time

from mqtt_client import MQTT_Client
from Audio import recorder, playback
from stmpy import Driver, Machine
from threading import Thread

class Coordinator:
    def __init__(self):
        self.channel = "team2"
        self.priority = 0
        self.client = MQTT_Client()
        self.client.start('mqtt.item.ntnu.no', 1883)
        self.client.client.subscribe(self.channel)

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

    def send_msg(self):
        print("sending message")
        #?? send(s)
        self.client.client.publish(self.channel, "message")
        #self.client.publish_recorded_message(self.channel, self.priority, filename)


    def set_new_channel(self):
        print("setting new channel")
        #Get chosen channel on gui
        self.client.client.unsubscribe(self.channel)
        chosen_channel = "team2/channel1"
        self.channel = chosen_channel
        self.client.client.subscribe(chosen_channel)


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
      'target': 'ready_to_send'}

t5 = {'trigger':'end_recording_button',
      'source': 'recording',
      'target': 'ready_to_send'}

t6 = {'trigger':'cancel_button',
      'source': 'ready_to_send',
      'target': 'idle'}

t7 = {'trigger':'send_button',
      'source': 'ready_to_send',
      'target': 'sending'}

t8 = {'trigger':'t1',
      'source': 'playing',
      'target': 'idle'}

t9 = {'trigger':'stop_button',
      'source': 'playing',
      'target': 'idle'}

t10 = {'trigger':'sending_failed',
      'source': 'sending',
      'target': 'ready_to_send'}

t11 = {'trigger':'sending_success',
      'source': 'sending',
      'target': 'idle'}

idle = {'name': 'idle', 'change_channel': 'set_new_channel'}

recording = {'name': 'recording',
             'entry': 'start_recording; start_timer("t3", 180000); ',
             'exit': 'end_recording',
             'new_incoming_msg': 'defer'}

ready_to_send = {'name': 'ready_to_send',
                 'new_incoming_msg': 'defer'}

sending = {'name': 'sending',
           'entry': 'send_msg',
           'new_incoming_msg': 'defer'
           }

playing = {'name': 'playing',
           'entry': 'start_timer("t1", 10000); play_msg',
           'new_incoming_msg': 'defer'}

machine = Machine(name='coordinator', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11], obj=coordinator, states=[idle, recording, ready_to_send, playing, sending])
coordinator.stm = machine

driver = Driver()
driver.add_machine(machine)
coordinator.client.stm_driver = driver

recorderInstance = recorder.Recorder(driver)
driver.add_machine(recorderInstance.stm)
driver.add_machine(playback.playback_stm)
driver.start()
coordinator.stm_driver = driver
playback.player.stm_driver = driver

#Just used to test the recorder.py atm -Toni
#driver.send("start", "recorder_stm")
#time.sleep(3)
#driver.send("stop", "recorder_stm")


