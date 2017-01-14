#!/usr/bin/env python3

from widgets.memory import MemoryWidget
from widgets.stretcher import StretcherWidget
from widgets.tags import TagsWidget
from widgets.spacer import SpacerWidget
from widgets.text import TextWidget
from widgets.battery import BatteryWidget
from widgets.clock import ClockWidget
from widgets.mpc import MpcWidget
from widgets.notmuch import NotmuchWidget
from widgets.title import TitleWidget
from panel import Panel

panel = Panel()

stretcher = StretcherWidget(panel)
spacer = SpacerWidget(panel, 20)
tags = TagsWidget(panel)
clock = ClockWidget(panel, '<normal>{t.day}<inactive>.{t.month}.{t.year} <normal>{t.hour:02d}:{t.minute:02d}')
mem = MemoryWidget(panel, '<normal>{used} <inactive>({available})')
battery = BatteryWidget(panel, '<inactive>{b[0][icon]} <normal>{b[0][percent]} <inactive>({b[0][time]})')
hello_world = TextWidget(panel, "<inactive>This is a <normal>very cocky<inactive> panel.py")
mpc = MpcWidget(panel, "<normal>%title%<inactive> (%artist%)")
notmuch = NotmuchWidget(panel, "<normal>{}<inactive> unread", "tag:inbox AND tag:unread AND NOT tag:killed")
title = TitleWidget(panel)

panel.register(tags)
panel.register(stretcher)
panel.register(title)
panel.register(stretcher)
panel.register(mpc)
panel.register(spacer)
panel.register(notmuch)
panel.register(spacer)
panel.register(mem)
panel.register(spacer)
panel.register(battery)
panel.register(spacer)
panel.register(clock)

panel.start()
