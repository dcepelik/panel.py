#!/usr/bin/env python3

from threading import Thread, Lock
from time import sleep
from util import hc, cmd
import re
import sys

class Widget:
    
    def __init__(self, panel, name):
        self.panel = panel
        self.name = name
        self.invalid = False
        self.cache = None
        self.cache_lock = Lock()

    def start(self):
        self.invalidate()
        self.thread = Thread(None, self.loop, "{}-loop".format(self.name))
        self.thread.daemon = True
        self.thread.start()

    def render(self):
        with self.cache_lock:
            if self.invalid:
                self.cache = self.do_render()
                self.invalid = False

        return self.cache

    def do_render(self):
        return str()

    def measure_width(self, font):
        text_no_markup = re.sub('\<[^\>]+\>', '', self.render())
        text_no_markup = re.sub('\^[^\(]*\([^\)]*\)', '', text_no_markup)
        return int(cmd('textwidth', font, text_no_markup))

    def invalidate(self):
        with self.cache_lock:
            self.invalid = True

        self.panel.invalidate(self)


class StaticWidget(Widget):
    
    def __init__(self, panel, name):
        super().__init__(panel, name)

    def loop(self):
        pass


class SimpleWidget(Widget):
    
    def __init__(self, panel, name, interval, cache = True):
        super().__init__(panel, name)
        self.interval = interval
        self.name = name

    def loop(self):
        while True:
            self.invalidate()
            sleep(self.interval)

geom_x, geom_y, geom_width, geom_height = map(int, hc('monitor_rect', '0').split(' '))
panel_height = 16
panel_width = geom_width
