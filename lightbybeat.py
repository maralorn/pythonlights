#!/usr/bin/python3

import pythonlights
import sound
import numpy as np

ctrl = pythonlights.LEDControl()
listener = sound.Listener()

peaks = np.array([50000000/256, 5000000/256, 5000000/256])
shortmean = np.array([128, 128, 128])
longmean = np.array([128, 128, 128])

sound.INPUT_BLOCK_TIME = 0.1
while True:
    spectrum = listener.get_spectrum()
    n = len(spectrum)
    a = int(250*sound.INPUT_BLOCK_TIME) # number of values amounting to 250 Hz
    colors = np.array([np.sum(spectrum[0:a]),np.sum(spectrum[a:a*2]),np.sum(spectrum[a*2:a*4])])
    colors /= peaks
    colors = np.clip(colors,0,255)
    shortmean = 0.7 * colors + 0.3 * shortmean
    longmean = 0.01 * colors + 0.99 * longmean
    peaks *= 0.01*longmean/128 + 0.99
    print(longmean,shortmean, peaks)
    color = pythonlights.Color(shortmean.astype(int))
    ctrl.set_all(color)
    ctrl.send()
