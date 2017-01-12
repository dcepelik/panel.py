from widgets.widget import SimpleWidget
from util import shell_cmd
import re

class BatteryWidget(SimpleWidget):

    def __init__(self, panel, fmt):
        super().__init__(panel, "memory", 10)
        self.fmt = fmt

    def do_render(self):
        icon_w = 18
        icon_h = 9

        batts = []
        for line in shell_cmd('acpi -b').splitlines():
            batid, status, percent, time = (re.split('[,:]? ', line) + [None])[1:5]

            if '[icon]' in self.fmt:
                full = int(icon_w * (float(percent.replace('%', '')) / 100.0))
                icon = '^r(2x5)^ro({icon_w}x{icon_h})^p(-{icon_w})^r({full:d}x{icon_h})^p({empty:d})'.format(
                    icon_w=icon_w,
                    icon_h=icon_h,
                    full=full,
                    empty=(icon_w - full),
                )

                self.extra_width = 3 + icon_w
                
            batts.append({
                'status': status,
                'percent': percent,
                'time': time,
                'icon': icon
            })

        return self.fmt.format(b=batts)
