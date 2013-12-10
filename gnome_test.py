import pythonlights
import math
import time

ctrl = pythonlights.LEDUtils()

while True:
	for t in range(0,100):
		ctrl.set_gnome(max(5,int(255*math.cos(2.0*t/200*math.pi)**2)))
		ctrl.send()
		time.sleep(0.02)
