#!/usr/bin/python

# open a microphone in pyAudio and get its FFT spectrum

import pyaudio
import numpy as np

FORMAT = pyaudio.paInt16 
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)

soundtype = np.dtype([('l',np.int16),('r',np.int16)])

class Listener(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()

    def stop(self):
        self.stream.close()

    def open_mic_stream( self ):
        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = None,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError:
            return
        return block


    # Returns the FFT of a sound sample recorded over INPUT_BLOCK_TIME.
    # This is a numpy array of RATE*INPUT_BLOCK_TIME/2 values.
    # The i-th element represents the frequency i/INPUT_BLOCK_TIME

    def get_spectrum(self):
        raw = self.listen()
        stereodata = np.fromstring(raw,soundtype)
        monodata = (stereodata['l'] + stereodata['r'])/2
        return abs(np.fft.rfft(monodata))
