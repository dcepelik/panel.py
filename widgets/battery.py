from widgets.widget import SimpleWidget
from util import shell_cmd
import re

class BatteryWidget(SimpleWidget):

    def __init__(self, panel, fmt):
        super().__init__(panel, "memory", 10)
        self.fmt = fmt

    def do_render(self):
        batteries = [ dict(zip(['status', 'percent', 'time'], re.split('[,:]? ', line)[2:] + [None]))
            for line in shell_cmd('acpi -b').split('\n') ]
        return self.fmt.format(b=batteries)
