#!/usr/bin/python3

import pythonlights
import sound
import numpy as np
import math

ctrl = pythonlights.LEDControl()
listener = sound.Listener()

max = 50000000/256
while True:
    spectrum = listener.get_spectrum()
    n = len(spectrum)
    a = int(n/3)
    b = np.sum(spectrum[0:a])/max
    g = np.sum(spectrum[a:a*2])/max
    r = np.sum(spectrum[a*2:a*3])/max
    print('red:',r,'green',g,'blue',b)

    white = math.max(b,255)
    color = pythonlights.Color(white,white,white)
    crtl.set_all(color)
    crtl.send()
