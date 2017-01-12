from widgets.stretcher import StretcherWidget
from threading import Event
from subprocess import Popen, PIPE
from util import hc
import sys
import re

font = "-*-Bitstream Vera Sans Mono-*-*-*-*-11-*-*-*-*-*-*-*"                                        
dzen2_opts = [ '-fn', font, '-ta', 'l' ]

class Panel:
    
    def __init__(self):
        self.widgets = []
        self.invalid = Event()
        self.load_styles()

    def load_styles(self):
        self.styles = {
            'normal': {
                'fg': '#efefef',
                'bg': '#000000',
            },

            'active': {
                'fg': '#000000',
                'bg': hc('get', 'window_border_active_color'),
            },

            'inactive': {
                'fg': '#888888',
                'bg': '#000000',
            },

            'urgent': {
                'fg': '#000000',
                'fg': '#ff0657',
            }
        }

    def invalidate(self, widget):
        self.invalid.set()

    def register(self, widget):
        self.widgets.append(widget)

    def format(self, text):
        output = str()
        for piece in re.split('(\<[^\>]+\>)', text):
            match = re.match('\<([^\>]+)\>', piece)
            if match:
                style_name = match.group(1)

                try:
                    style = self.styles[style_name]
                    output = output + '^fg({})^bg({})'.format(style['fg'], style['bg'])
                except KeyError:
                    sys.stderr.write('Unknown style: {}\n'.format(style_name))
            else:
                output += piece

        return output

    def render(self):
        total_width = 0
        num_stretchers = 0
        outputs = []
        for widget in self.widgets:
            output = widget.render(font)
            total_width += widget.get_rendered_width()
            outputs.append(self.format(output))

            if isinstance(widget, StretcherWidget):
                num_stretchers += 1

        dzen_input = ''
        for widget in self.widgets:
            dzen_input += outputs.pop(0)
            if isinstance(widget, StretcherWidget):
                dzen_input += "^p({})".format((1920 - total_width) / num_stretchers)

        assert not outputs
        dzen_input += '\n'

        self.dzen2.stdin.write(dzen_input.encode())
        self.dzen2.stdin.flush()

    def start(self):
        self.dzen2 = Popen(['dzen2'] + dzen2_opts, stdin=PIPE, stdout=PIPE)
        
        for widget in self.widgets:
            widget.start()

        while True:
            self.invalid.wait()
            self.invalid.clear()
            self.render()
