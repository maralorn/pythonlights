#!/usr/bin/python3

import socket

HOST = '2.0.0.2'
PORT = 6454
HEADER = b'Art-Net' + bytearray((00, # Protocol Name
    00, 80, # Opcode
    00, 14, # Protocol Version
    00,     # Sequence
    00,     # Physical
    00, 00, # Universe
    00, 80))# Payload length (5 Panels with 16 channels)
print(repr(HEADER))

# panel: 0-4
# position: 0-4
# color: {0: red, 1: green, 2:blue}
def get_led_number(panel, position, colorid):
    if type(panel) != int or type(position) != int or type(colorid) != int:
        raise TypeError("Panel, position and colorid have to be integers. They were: {0},{1},{2}".format(type(panel),type(position),type(colorid)))
    if panel < 0 or panel > 4:
        raise ValueError("There are only 5 panels. Pick from 0 to 4. Not {0}".format(panel))
    if position < 0 or position > 4:
        raise ValueError("There are only 5 positions in a panel. Pick from 0 to 4. Not {0}".format(position))
    if colorid < 0 or colorid > 2:
        raise ValueError("Only 0 for red, 1 for green and 2 for blue are valid color ids. Not {0}".format(colorid))
    return panel*16+position*3+colorid+1


class Color(object):
    def __init__(self, *args):
        if args[0]:
            if type(args[0]) == str:
                self.parse_string(args[0])
            if type(args[0]) == tuple:
                self.values = list(args[0])
        else:
            self.values = [0,0,0]

    def parse_string(self, string):
        if string[0] == "#":
            split = (string[1:3], string[3:5], string[5:7])
            self.values = [int(x, 16) for x in split]
        else:
            raise ValueError("Unkown color format '{0}'".format(string))

# LED Controller for the troll cave.
# Color parameters take a string (currently only "#rrggbb" format), tuple of 3 integers in [0,255] or Color objects.

class LEDControl(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((HOST, PORT))
        self.state = [255 for i in range(80)]
    
    def send(self):
        package = HEADER+bytearray(self.state)
        self.socket.send(package)

    def set_intensity(self, panel, position, colorid, value):
        if type(value) != int:
            raise TypeError('Color Value has to be an integer.')
        if value < 0 or value > 255:
            raise ValueError('Color Value has to be in [0,255]. Not {0}'.format(value))
        self.state[get_led_number(panel, position, colorid)] = value

    def get_intensity(self, panel, position, colorid):
        return self.state[get_led_number(panel, position, colorid)]

    def set_color(self, panel, position, color):
        if type(color) != Color:
            color = Color(color)
        for colorid, value in enumerate(color.values):
            self.set_intensity(panel, position, colorid, value)
    
    def set_position(self, position, color):
        for panel in range(5):
            self.set_color(panel, position, color)

    def set_panel(self, panel, color):
        for position in range(5):
            self.set_color(panel, position, color)

    def set_all(self, color):
        for panel in range(5): 
            self.set_panel(panel, color)

class LEDUtils(LEDControl):
    def all_on(self):
        self.set_all('#ffffff')
        self.send()
    
    def all_off(self):
        self.set_all('#000000')
        self.send()

# test:
if __name__ == "__main__":
    utils = LEDUtils()
    utils.set_all("#FF9933")
    utils.send()
