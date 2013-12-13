#!/usr/bin/python3
# -*- coding: utf-8 -*-


import pythonlights
import sound
import numpy as np
import math

ctrl = pythonlights.LEDUtils()
listener = sound.Listener()

ones = np.ones(25)
peaks = 65000 # Nur ein Schätzwert
shortmean = ones # long zum regeln, short zum glätten
colors = np.array(ones)

sound.INPUT_BLOCK_TIME = 0.04

def interval_border(i):
	return int(80.0*(15000.0/80)**(1.0*i/25)*sound.INPUT_BLOCK_TIME)

default = 255
exponent = 0.5
calm = 0.3



frequency = 0.27
phase = 0
def rainbow(i, intensity):
   red   = math.sin(-frequency*i - 3.5*math.pi/3 + phase) * 127 + 128;
   green = math.sin(-frequency*i - 1.5*math.pi/3 + phase) * 127 + 128;
   blue  = math.sin(-frequency*i + 0.5*math.pi/3 + phase) * 127 + 128;
   return [int(red*intensity+(1-intensity)*default), int(green*intensity+(1-intensity)*default), int(blue*intensity+(1-intensity)*default)]
    
ctrl.set_gnome(0)
try:
    while True:
        # Dieser Aufruf blockt, bis genug sample da ist.
        spectrum = listener.get_spectrum()
    
        for i in range(25):
            if interval_border(i+1)-interval_border(i) > 0:
#                colors[i] = np.sum(spectrum[interval_border(i):interval_border(i+1)])/(interval_border(i+1)-interval_border(i))
                colors[i] = np.sum(spectrum[interval_border(i):interval_border(i+1)])
            else:
                colors[i] = 0
        peaks = (0.01 * max(colors)) + 0.99 * peaks
             
    
        # Normalisiere auf anzeigbare Intensitäten
        colors /= peaks 
        colors = 1 - (1 - np.clip(colors,0,1))**exponent
    
        # gleitende Mittelwerte
        shortmean = calm * colors + (1-calm) * shortmean
    
        # Einstellen und senden der berechneten Farbe.
        for i in range(25):
            color = pythonlights.Color(rainbow(i, shortmean[i]))
            ctrl.set_pos_in_circ(i, color)
        ctrl.send()
        #phase += 0.05
except KeyboardInterrupt:
    ctrl.all_on()
