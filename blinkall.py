#!/usr/bin/python3

from pythonlights import LEDUtils
from time import sleep

u = LEDUtils()
u.all_off()

while True:
  for position in range(5):
		  u.set_position(position, "#ffffff")
		  u.send()
		  sleep(0.5)
		  u.set_position(position, "#000000")
		  u.send()
