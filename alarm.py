import time
import pythonlights

def red(i, pos):
    return max(255-15*( (i-pos)%25 )**2, 0)

pos=0
l = pythonlights.LEDUtils()
try:
    while True:
        for i in range(0,25):
            l.set_color(i // 5, i % 5, [red(i,pos), 0, 0])
            #l.set_color(i // 5, i % 5, [125+red(i,pos)//2, 255-red(i,pos)//2, 255-red(i,pos)//2])
        l.send()
        time.sleep(0.05)
        pos = (pos + 1) % 25
except KeyboardInterrupt:
    l.all_on()
