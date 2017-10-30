from widgets.widget import Widget
from util import shell_cmd

class MpcWidget(Widget):
    
    def __init__(self, panel, fmt):
        super().__init__(panel, "mpc")
        self.fmt = fmt
        self.first = True
        self.current_song = ''

    def do_render(self):
        return self.current_song

    # On first render, don't wait for an MPC event to occur.
    # On subsequent renders, use --wait instead of polling.
    def loop(self):
        while True:
            self.current_song = shell_cmd('mpc -f "{}" {} current'.format(self.fmt, '--wait' if not self.first else ''))
            self.first = False
            self.invalidate()
