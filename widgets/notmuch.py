from widgets.widget import SimpleWidget
from util import cmd

class NotmuchWidget(SimpleWidget):

    def __init__(self, panel, fmt, query, interval=3):
        super().__init__(panel, fmt, interval)
        self.fmt = fmt
        self.query = query

    def do_render(self):
        num_msgs = cmd('notmuch', 'count', '--output=messages', self.query)
        return self.fmt.format(num_msgs) if int(num_msgs) > 0 else 'No mail'
