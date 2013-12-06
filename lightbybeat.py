#!/usr/bin/python3

import pythonlights
import sound
import numpy as np

ctrl = pythonlights.LEDControl()
listener = sound.Listener()

peak = 50000000/256
while True:
    spectrum = listener.get_spectrum()
    n = len(spectrum)
    a = int(n/3)
    b = np.sum(spectrum[0:a])/peak
    g = np.sum(spectrum[a:a*2])/peak
    r = np.sum(spectrum[a*2:a*3])/peak

    print(r,g,b)
    white = max(b,255)
    color = pythonlights.Color((white,white,white))
    ctrl.set_all(color)
    ctrl.send()
