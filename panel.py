from widgets.stretcher import StretcherWidget
from threading import Event
from subprocess import Popen, PIPE
from util import hc
import sys
import re

font = "-*-Bitstream Vera Sans Mono-*-*-*-*-10-*-*-*-*-*-*-*"                                        

class Panel:
    
    def __init__(self):
        self.widgets = []
        self.invalid = Event()
        self.load_styles()

    def load_styles(self):
        self.styles = {
            'normal': {
                'fg': '#FFFFFF',
                'bg': '#000000',
            },

            'active': {
                'fg': '#000000',
                'bg': '#FFFFFF',
            },

            'inactive': {
                'fg': '#bbbbbb',
                'bg': '#000000',
            },

            'urgent': {
                'bg': '#7B0000',
                'fg': '#FFFFFF',
            }
        }

        self.dzen2_opts = [
            '-fn', font,
            '-ta', 'l',
            '-bg', self.styles['normal']['bg']
        ]

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
                dzen_input += "^p({})".format((self.width - total_width) / num_stretchers)

        assert not outputs
        dzen_input += '\n'

        self.dzen2.stdin.write(dzen_input.encode())
        self.dzen2.stdin.flush()

    def start(self):
        monitor_no = sys.argv[1]
        geom_x, geom_y, geom_width, geom_height = map(int, hc('monitor_rect', monitor_no).split(' '))
        self.height = 15
        self.width = geom_width
        self.dzen2 = Popen(['dzen2'] + self.dzen2_opts + [
            '-tw', str(self.width),
            '-x', str(geom_x)
        ], stdin=PIPE, stdout=PIPE)

        hc('pad', str(monitor_no), str(self.height))
        
        for widget in self.widgets:
            widget.start()

        while True:
            self.invalid.wait()
            self.invalid.clear()
            self.render()
