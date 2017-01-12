from widgets.widget import Widget
from threading import Lock
from subprocess import Popen, PIPE
from util import hc, colors
import re
import sys

class TagsWidget(Widget): 
    def __init__(self, panel):
        super().__init__(panel, "tags")
        self.lock = Lock()
        self.load_tags()
        self.load_windows()

    def load_tags(self):
        self.tags = { tag[1:]: { 'name': tag[1:] } for tag in hc('tag_status').split('\t') }
        self.refresh_tags()

    def refresh_tags(self):
        for tag in hc('tag_status').split('\t'):
            self.tags[tag[1:]]['status'] = tag[0]


    def load_window(self, winid):
        self.windows[winid] = {}
        attrs = hc('attr', 'clients.{}'.format(winid)).splitlines();
        for attr in attrs:
            match = re.match('^ \w [\w-] (\w+)\s*= "?([^"]+)"?$', attr)
            if match:
                self.windows[winid][match.group(1)] = match.group(2)

        if len(self.windows[winid]) == 0:
            self.windows.remove(winid)

    def rebuild_dynamic_names(self):
        for tag in self.tags.values():
            tag_apps = set()

            for window in filter(lambda w: w['tag'] == tag['name'], self.windows.values()):
                if not 'title' in window:
                    sys.stderr.write('No title for this window, why?\n')
                    window['title'] = ''

                app_name = None
                if window['class'].lower() == 'termite':
                    pieces = window['title'].split(' ')

                    for word in filter(lambda p: re.match("^\w+$", p), pieces):
                            if word != 'sudo':
                                app_name = word.lower()
                                break

                    if pieces[-1] == 'VIM' or pieces[-1] == 'NVIM':
                        match = re.match('^([^\(]*) \(.*\) - N?VIM$', window['title'])
                        if match:
                            app_name = '[{}]'.format(re.sub(' [+=]?$', '', match.group(1)))

                else:
                    app_name = window['class'].strip().lower()

                if app_name:
                    tag_apps.add(app_name)

            tag['dynamic_name'] = '+'.join(sorted(tag_apps))

    def load_windows(self):
        self.windows = {}

        clients = [ winid.strip() for winid in hc('attr', 'clients').splitlines() ]
        num_clients = int(clients[0].split(' ')[0])

        for winid in clients[1:num_clients + 1]:
            self.load_window(winid)

        self.rebuild_dynamic_names()


    def do_render(self):
        self.lock.acquire()

        tag_names = []
        for tag in self.tags.values():

            status_to_style = {
                '#': 'active',
                ':': 'normal',
                '.': 'inactive',
                '!': 'urgent'
            }
        
            tag_names.append('<{}> {}{}{} <normal>'.format(
                status_to_style[tag['status']],
                tag['name'],
                ':' if tag['dynamic_name'] else '',
                tag['dynamic_name'],
            ))

        self.lock.release()
        return ' '.join(tag_names)


    def loop(self):
        with Popen(['herbstclient', '-i'], stdout=PIPE) as hc:
            for event in hc.stdout:
                ev_type, ev_arg = (event.decode().split('\t') + [None])[0:2]

                if ev_type == 'tag_flags' or (ev_type == 'focus_changed' and ev_arg != '0x0'):
                    continue

                with self.lock:
                    if ev_type == 'window_title_changed':
                        # optimization candidate: only reload the window whose title changed
                        self.load_windows()
                    elif ev_type == 'urgent' or ev_type == 'tag_changed' or ev_type == 'tag_flags':
                        self.refresh_tags()
                    elif ev_type == 'focus_changed':
                        self.load_windows()

                self.invalidate()
