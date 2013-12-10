#!/usr/bin/python3
# -*- coding: utf-8 -*-


import pythonlights
import sound
import numpy as np

ctrl = pythonlights.LEDControl()
listener = sound.Listener()

ones = np.ones(3)
#peaks = ones * 50000000/256 # Nur ein Schätzwert
peaks=0;
longmean = shortmean = ones * 128 # long zum regeln, short zum glätten
#
sound.INPUT_BLOCK_TIME = 0.1
a = int(250*sound.INPUT_BLOCK_TIME) # Anzahl der Array Element um 250Hz abdecken

while True:
    # Dieser Aufruf blockt, bis genug sample da ist.
    spectrum = listener.get_spectrum()

    # blau 0-250 Hz, grün 250-500 Hz, rot 500-1000 Hz
    colors = np.array([np.sum(spectrum[0:a]),np.sum(spectrum[a:a*6]),np.sum(spectrum[a*6:a*15])-np.sum(spectrum[a*2:a*6])]) 
    peaks*=0.99;
    peaks = np.max(np.array([colors[0],colors[1],colors[2],peaks]));
    # Normalisiere auf anzeigbare Intensitäten
    colors /= (peaks/256+1); 
    colors = np.clip(colors,0,255)

    # gleitende Mittelwerte
    shortmean = 0.5 * colors + 0.5 * shortmean
    longmean = 0.01 * colors + 0.99 * longmean

    # Korrektur der Maximalwerte um damit die Intesitäten im Mittel um 50% schwanken.
#    peaks *= 0.01*longmean/128 + 0.99 

    # Einstellen und senden der berechneten Farbe.
    color = pythonlights.Color(shortmean.astype(int))
    ctrl.set_all(color)
    ctrl.send()
