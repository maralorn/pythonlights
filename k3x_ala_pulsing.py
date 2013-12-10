import time
import pythonlights

up=True
pos=0
try:
    while True:
        print pos
        l = pythonlights.LEDControl()
        for i in range(0,25):
            l.set_color(i // 5, i % 5, [pos,0,0])
        l.send()
        time.sleep(0.005)
        if up:
            pos = (pos+1.5)
        else: 
            pos = (pos-1.5)
        if pos>=255: up=False
        if pos<=0: up=True
except KeyboardInterrupt:
    l = pythonlights.LEDUtils()
    l.all_on()
