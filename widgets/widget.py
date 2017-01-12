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
        self.cache_width = 0
        self.extra_width = 0
        self.cache_lock = Lock()

    def start(self):
        self.invalidate()
        self.thread = Thread(None, self.loop, "{}-loop".format(self.name))
        self.thread.daemon = True
        self.thread.start()

    def render(self, font):
        with self.cache_lock:
            if self.invalid:
                self.cache = self.do_render()
                text_no_markup = re.sub('\<[^\>]+\>|\^[^\(]*\([^\)]*\)', '', self.cache)
                self.cache_width = int(cmd('textwidth', font, text_no_markup))

                self.invalid = False

        return self.cache

    def do_render(self):
        return str()

    def get_rendered_width(self):
        return self.cache_width + self.extra_width

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
    
    def __init__(self, panel, name, interval):
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
