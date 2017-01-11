from widgets.widget import SimpleWidget
from util import shell_cmd
import re

class MemoryWidget(SimpleWidget):
    
    def __init__(self, panel, fmt):
        super().__init__(panel, "memory", 10)
        self.fmt = fmt

    def do_render(self):
        mem = re.split(' +', shell_cmd('free -h --mebi | sed -n 2p'))
        return self.fmt.format(total=mem[1], used=mem[2], free=mem[3], available=mem[6])
