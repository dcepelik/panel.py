#!/usr/bin/env python3

from widgets.memory import MemoryWidget
from widgets.stretcher import StretcherWidget
from widgets.tags import TagsWidget
from widgets.spacer import SpacerWidget
from widgets.text import TextWidget
from widgets.battery import BatteryWidget
from widgets.clock import ClockWidget
from widgets.mpc import MpcWidget
from panel import Panel

panel = Panel()

stretcher = StretcherWidget(panel)
spacer = SpacerWidget(panel, 15)
tags = TagsWidget(panel)
clock = ClockWidget(panel, '<normal>{t.day}<inactive>.{t.month}.{t.year} <normal>{t.hour:02d}:{t.minute:02d}')
mem = MemoryWidget(panel, '<normal>{used} <inactive>({available})')
battery = BatteryWidget(panel, '<normal>{b[0][percent]} <inactive>({b[0][time]})')
hello_world = TextWidget(panel, "<inactive>This is a <normal>very cocky<inactive> panel.py")
mpc = MpcWidget(panel, "<normal>%title%<inactive> (%artist%)")

panel.register(tags)
panel.register(stretcher)
panel.register(hello_world)
panel.register(stretcher)
panel.register(mpc)
panel.register(spacer)
panel.register(mem)
panel.register(spacer)
panel.register(battery)
panel.register(spacer)
panel.register(clock)

panel.start()
