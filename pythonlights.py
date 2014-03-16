#!/usr/bin/python2

import socket
import time
import random
import threading

HOST = '2.0.0.2'
PORT = 6454
HEADER = b'Art-Net' + bytearray((00,  # Protocol Name
                                 00, 80,  # Opcode
                                 00, 14,  # Protocol Version
                                 00,  # Sequence
                                 00,  # Physical
                                 00, 00,  # Universe
                                 00, 80))  # Payload length (5 Panels with 16 channels)

# panel: 0-4
# position: 0-4
# color: {0: red, 1: green, 2:blue}
def get_led_number(panel, position, colorid):
    if panel < 0 or panel > 4:
        raise ValueError("There are only 5 panels. Pick from 0 to 4. Not {0}".format(panel))
    if position < 0 or position > 4:
        raise ValueError("There are only 5 positions in a panel. Pick from 0 to 4. Not {0}".format(position))
    if colorid < 0 or colorid > 2:
        raise ValueError("Only 0 for red, 1 for green and 2 for blue are valid color ids. Not {0}".format(colorid))
    return int(panel) * 16 + int(position) * 3 + int(colorid) + 1


class Color(object):
    # Takes a string '#rrggbb' or a iterable of 3 integers
    def __init__(self, values=None):
        if values is not None:
            if type(values) == str:
                self.parse_string(values)
            else:
                self.values = list(values)
        else:
            self.values = [0, 0, 0]

    def parse_string(self, string):
        if string[0] == "#":
            string = string[1:]
        try:
            split = (string[0:2], string[2:4], string[4:6])
            self.values = [int(x, 16) for x in split]
        except:
            raise ValueError("Unkown color format '{0}'".format(string))

    def get_complementary_color(self):
        a = 1 - (0.299 * self.values[0] + 0.587 * self.values[1] + 0.114 * self.values[2]) / 255
        if a < 0.5:
            d = 0
        else:
            d = 255
        return [d, d, d]

    def to_html(self, rgb):
        return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


# LED Controller for the troll cave.
# Color parameters take a string (currently only "#rrggbb" format), tuple of 3 integers in [0,255] or Color objects.

class LEDControl(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((HOST, PORT))
        self.state = [255 for i in range(80)]

    # Call this method or nothing will happen!!
    def send(self):
        package = HEADER + bytearray(self.state)
        self.socket.send(package)

    def set_intensity(self, panel, position, colorid, value):
        if value < 0 or value > 255:
            raise ValueError('Color Value has to be in [0,255]. Not {0}'.format(value))
        self.state[get_led_number(panel, position, colorid)] = int(value)

    def get_intensity(self, panel, position, colorid):
        return self.state[get_led_number(panel, position, colorid)]

    # Set color auf LED Tripel at specified position.
    def set_color(self, panel, position, color):
        if not isinstance(color, Color):
            color = Color(color)
        for colorid, value in enumerate(color.values):
            self.set_intensity(panel, position, colorid, value)

    # Set color auf LED Tripel at specified position on every panel.
    def set_position(self, position, color):
        for panel in range(5):
            self.set_color(panel, position, color)

    # Set color auf LED Tripel at all positions on one panel.
    def set_panel(self, panel, color):
        for position in range(5):
            self.set_color(panel, position, color)

    # Set color auf LED Tripel everywhere.
    def set_all(self, color):
        for panel in range(5):
            self.set_panel(panel, color)

    def set_gnome(self, intensity):
        self.state[64] = intensity

    def set_pos_in_circ(self, position, color):
        correct_pos = (position + 15) % 25
        self.set_color(correct_pos // 5, correct_pos % 5, color)


class LEDUtils(LEDControl):
    def all_on(self):
        self.set_all('#ffffff')
        self.send()

    def all_off(self):
        self.set_all('#000000')
        self.send()


class LEDPlugin(object):
    "Inherit this class, and implement the get_state method returning a list of colors with the length of mapping"
    name = "Plugin name not set"

    def __init__(self, priority=0, mapping=range(25), decay=None):
        self.id = random.randint(0, 2 ** 32 - 1)
        self.priority = priority
        self.mapping = mapping
        self.decay = decay
        self.options = {}
        self.lock = threading.RLock()
        self.lock.acquire()
        self.init()
        self.lock.release()

    def init(self):
        pass

    def get_option(self, name):
        self.lock.acquire()
        value = self.options[name]['value']
        self.lock.release()
        return value

    def get_options(self):
        self.lock.acquire()
        value = self.options.keys()
        self.lock.release()
        return value

    def set_option(self, name, value):
        self.lock.acquire()
        try:
            self.options[name]['value'] = self.options[name]['type'](value)
        except ValueError:
            print("Invalid value caught in set_option(...): {}".format(value))
        self.lock.release()

    def get_state(self):
        return [Color((0, 0, 0)) for i in self.mapping]

    def get_state_safe(self):
        self.lock.acquire()
        state = self.get_state()
        self.lock.release()
        return state

    def register_option(self, name, typ, default, display_name=None, comment=""):
        if display_name is None:
            display_name = name
        self.options[name] = {"type": typ,
                              "value": default,
                              "display_name": display_name,
                              "comment": comment}

    def autoenable_condition(self):
        # -1 == disable,
        #  0 == unsupported
        #  1 == enable
        return 0


class LEDPluginMaster(LEDControl):
    registered_plugins = {}
    presets = {}

    def __init__(self):
        LEDControl.__init__(self)
        self.set_gnome(0)
        self.plugins = []
        self.color_state = []
        self.lock = threading.RLock()
        self.autotoggle_ts = time.time()

    def sort(self):
        self.lock.acquire()
        self.plugins.sort(key=lambda plugin: plugin.priority)
        self.lock.release()

    def send(self):
        self.lock.acquire()
        self.sort()
        new_state = {}
        for plugin in self.plugins[:]:
            if plugin.decay and plugin.decay < time.time():
                self.plugins.remove(plugin)
            else:
                plugin.state = plugin.get_state_safe()
                for key, index in enumerate(plugin.mapping):
                    self.set_pos_in_circ(index, plugin.state[key])
                    new_state[key] = plugin.state[key]
        self.color_state = new_state
        if len(self.plugins) > 0:
            LEDControl.send(self)
        self.lock.release()

    @classmethod
    def register_plugin(cls, class_):
        cls.registered_plugins[class_.name] = class_

    @classmethod
    def register_preset(cls, function):
        cls.presets[function.name] = function

    @classmethod
    def available_plugins(cls):
        return [name for name in cls.registered_plugins]

    @classmethod
    def available_presets(cls):
        return [name for name in cls.presets]

    def autotoggle_check(self):
        for name, plugin in LEDPluginMaster.registered_plugins.iteritems():
            try:
                p = plugin(0, range(25), None)
                state = p.autoenable_condition()
                if state == -1:
                    self.remove_plugin_by_name(name)
                elif state == 1:
                    if self.get_plugin_by_name(name) is None:
                        self.instanciate_plugin(name, 10)
                del p, state
            except Exception:
                pass

    def run_preset(self, name):
        self.lock.acquire()
        self.presets[name](self)
        self.lock.release()

    def instanciate_plugin(self, name, priority=0, mapping=range(25), decay=None):
        self.lock.acquire()
        plugin = LEDPluginMaster.registered_plugins[name](priority, mapping, decay)
        self.plugins.append(plugin)
        self.lock.release()
        return plugin

    def remove_plugin(self, pluginid):
        self.lock.acquire()
        self.plugins.remove(self.get_plugin(pluginid))
        self.lock.release()

    def remove_plugin_by_name(self, name):
        plugin = self.get_plugin_by_name(name)
        if plugin != None:
            self.remove_plugin(plugin.id)

    def get_plugin(self, pluginid):
        self.lock.acquire()
        plugin = None
        for plugin in self.plugins:
            if plugin.id == pluginid:
                break
        self.lock.release()
        return plugin

    def get_plugin_by_name(self, name):
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    def run(self):
        self.exit = False

        # init to a color that is friendly to the eye
        grey = Color([105, 105, 105])
        for i in range(25):
            self.set_pos_in_circ(i, grey)

        while not self.exit:
            self.update()
            time.sleep(0.02)

    def update(self):
        # query plugins and send new colors
        self.send()

        # check for auto-toggle
        now = time.time()
        diff = now - self.autotoggle_ts
        if diff > 5.0:
            #self.autotoggle_check()
            self.autotoggle_ts = now

    def clear(self):
        self.lock.acquire()
        self.plugins = []
        self.lock.release()


class Black(LEDPlugin):
    name = "Schwarz"

LEDPluginMaster.register_plugin(Black)


def aus(pm):
    pm.plugins = []
    pm.instanciate_plugin('Schwarz', decay=time.time() + 1)

#aus.name = 'Alles Aus'
#LEDPluginMaster.register_preset(aus)

def clear(pm):
    pm.plugins = []

clear.name = 'Clear'
LEDPluginMaster.register_preset(clear)

# test:
if __name__ == "__main__":
    utils = LEDUtils()
    utils.all_on()
