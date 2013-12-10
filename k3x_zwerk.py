import time
import pythonlights

l = pythonlights.LEDControl()
pos=0
l.set_all([60,60,60])
try:
    while True:
        l.set_color(3, 4, [0, 0, pos])
            #l.set_color(i // 5, i % 5, [125+red(i,pos)//2, 255-red(i,pos)//2, 255-red(i,pos)//2])
        l.send()
        time.sleep(0.02)
        pos = (pos + 3) % 255
except KeyboardInterrupt:
    l = pythonlights.LEDUtils()
    l.all_on()
