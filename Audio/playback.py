from stmpy import Machine, Driver
from os import system
import os
import time

import pyaudio
import wave


class Player:
    def __init__(self, parentDriver):
        self.parentDriver = parentDriver

        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
        t2 = {'trigger': 'done', 'source': 'playing', 'target': 'ready', 'effect':'finished_playing'}


        s_playing = {'name': 'playing', 'do': 'play(*)'}

        self.playback_stm = Machine(name='playback_stm', transitions=[t0, t1, t2], states=[s_playing], obj=self)
        pass

    def play(self, filename):
        print("Inside playback, playing "+filename)
        # Set chunk size of 1024 samples per data frame
        chunk = 1024

        # Open the sound file
        wf = wave.open(filename, 'rb')

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        # Read data in chunks
        data = wf.readframes(chunk)

        # Play the sound by writing the audio data to the stream
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)

        # Close and terminate the stream
        stream.close()
        p.terminate()
        wf.close()
        self.parentDriver.send('done','playback_stm')
        #self.finished_playing()
    
    def finished_playing(self):
        print("Called finished_playing")
        self.parentDriver.send('done_playing', 'coordinator')





