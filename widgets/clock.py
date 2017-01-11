from datetime import datetime
from widgets.widget import SimpleWidget

class ClockWidget(SimpleWidget):

    def __init__(self, panel, fmt):
        super().__init__(panel, "clock", 5)
        self.fmt = fmt

    def do_render(self):
        return self.fmt.format(t=datetime.now())
