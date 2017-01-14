from widgets.widget import Widget
from subprocess import Popen, PIPE

class TitleWidget(Widget):
    
    def __init__(self, panel, fmt = "<normal>{title}"):
        super().__init__(panel, "title")
        self.fmt = fmt
        self.cur_winid = None
        self.cur_title = None

    def do_render(self):
        if not self.cur_title:
            self.cur_title = str()
        return self.fmt.format(title=self.cur_title)

    def loop(self):
        with Popen(['herbstclient', '-i'], stdout=PIPE) as hc:
            for event in hc.stdout:
                ev_type, ev_arg1, ev_arg2 = (event.decode().strip().split('\t') + [None, None])[0:3]

                if ev_type == 'focus_changed':
                    self.cur_winid = ev_arg1
                    self.cur_title = ev_arg2
                elif ev_type == 'window_title_changed' and ev_arg1 == self.cur_winid:
                    self.cur_title = ev_arg2
                else:
                    continue

                self.invalidate()
