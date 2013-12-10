import time
import pythonlights

def red(i, pos):
    return max(255-15*( (i-pos)%25 )**2, 0)

pos=0
try:
    while True:
        print pos
        l = pythonlights.LEDControl()
        for i in range(0,25):
            l.set_color(i // 5, i % 5, [0,0,red(i,pos)])
        l.send()
        time.sleep(0.05)
        pos = (pos + 1) % 25
except KeyboardInterrupt:
    l = pythonlights.LEDUtils()
    l.all_on()
