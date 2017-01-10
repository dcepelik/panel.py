#!/usr/bin/env python3

from subprocess import check_output, Popen, PIPE
import re
import datetime
from time import sleep
from threading import Thread
from queue import Queue


def cmd(cmd):
    return check_output(cmd).strip().decode('utf-8')


def shellcmd(cmd):
    return check_output(cmd, shell=True).strip().decode('utf-8')


def hc(cmds):
    return check_output(['herbstclient'] + cmds).strip().decode('utf-8')


font = "-*-Bitstream Vera Sans Mono-*-*-*-*-11-*-*-*-*-*-*-*"                                        
dzen2_opts = [
    '-fn', font,
    '-ta', 'l'
]

fg_normal = '#efefef'
fg_selected = '#000000'
fg_fade = '#888888'
fg_urgent = fg_selected

bg_normal = '#000000' #hc(['get', 'window_border_normal_color'])
bg_selected = hc(['get', 'window_border_active_color'])
bg_fade = bg_normal
bg_urgent = '#FF0657'

panel_x, panel_y, panel_width, panel_height = map(int, hc(['monitor_rect', '0']).split(' '))

events = Queue()
status_check_delay = 3

def herbst_events():
    with Popen(['herbstclient', '-i'], stdout=PIPE) as herbstclient:
        for line in herbstclient.stdout:
            events.put({
                'name': line.decode().split('\t')[0]
            })


def status_events():
    while True:
        status = []

        net_name, net_if = shellcmd('nmcli --terse --fields "name,device" connection show --active').split(':')
        status.append('{}{}{}@{}'.format(
            colors(fg_normal, bg_normal),
            net_name,
            colors(fg_fade, bg_fade),
            net_if
        ))

        total_mem, free_mem = shellcmd("free -h --mebi | tail -n+2 | head -n1 | tr -s $' ' | cut -d' ' -f2,3").split(' ')
        status.append('{}{}{} / {}'.format(
            colors(fg_normal, bg_normal),
            free_mem,
            colors(fg_fade, bg_fade),
            total_mem
        ))

        battery = shellcmd("acpi -b | head -n1 | cut -d' ' -f4,5").split(', ')
        if len(battery) == 2:
            percent, time = battery
            status.append('{}{}{} ({})'.format(
                colors(fg_normal, bg_normal),
                percent,
                colors(fg_fade, bg_fade),
                time
            ))

        now = datetime.datetime.now()
        status.append('{}{}{}.{}.{} {}{}:{}'.format(
            colors(fg_normal, bg_normal),
            now.day,
            colors(fg_fade, bg_fade),
            now.month,
            now.year,
            colors(fg_normal, bg_normal),
            now.hour,
            now.minute
        ))

        events.put({
            'name': 'status_changed',
            'status':  '   '.join(status)
        })
        sleep(status_check_delay)


def colors(fg, bg):
    return '^fg({})^bg({})'.format(fg, bg)


def load_tags():
    return str.split(hc(['tag_status']), '\t')


def get_attr(attrs, name):
    for attr in attrs:
        if name in attr:
            return attr.split('=')[1].strip()

def load_windows():
    windows = dict()

    clients = hc(['attr', 'clients']).split('\n')
    num_clients = int(clients[0].split(' ')[0])

    for winID in clients[1:num_clients + 1]:
        winID = winID.strip()[:-1]
        attrs = hc(['attr', 'clients.{}.'.format(winID.strip())]).split('\n')

        windows[winID] = {
            'title': get_attr(attrs, 'title'),
            'class': get_attr(attrs, 'class'),
            'instance': get_attr(attrs, 'instance'),
            'pid': get_attr(attrs, 'pid')
        }

    return windows


def text_width(string):
    string_no_cmds = re.sub('\^[^\(]*\([^\)]*\)', '', string)
    return int(cmd(['textwidth', font, string_no_cmds]))


herbst_thread = Thread(target=herbst_events)
herbst_thread.daemon = True
status_thread = Thread(target=status_events)
status_thread.daemon = True

herbst_thread.start()
status_thread.start()

with Popen(['dzen2'] + dzen2_opts, stdin=PIPE, stdout=PIPE) as dzen2:
    tag_statuses = load_tags()
    windows = load_windows()
    status = None

    while True:
        event = events.get()

        print(event['name'])

        if event['name'] == 'tag_changed':
            tag_statuses = load_tags()
        elif event['name'] == 'window_title_changed':
            windows = load_windows()
        elif event['name'] == 'status_changed':
            status = event['status']
            windows = load_windows()
        else:
            continue

        tags = []

        # tags and windows 

        for tag in tag_statuses:
            tag_status = tag[0:1]
            name = tag[1:]

            layout = hc(['dump', name])
            
            apps = set()

            for winID in re.findall('0x[0-9a-fA-F]+', layout, re.MULTILINE):
                try:
                    win = windows[winID]

                    app_name = None
                    if win['class'] == 'Termite':
                        pieces = win['title'].replace('\"', '').split(' ')

                        for piece in pieces:
                            if re.match('^\w+$', piece):
                                app_name = piece.lower().strip()

                                # skip 'sudo'
                                if app_name == 'sudo':
                                    continue

                                break

                        # get edited file name (requires 'set title')
                        if pieces[-1] == 'VIM':
                            match = re.match('^([^\(]*) \(.*\) - VIM$', win['title'].replace('\"', ''))
                            if match:
                                app_name = '[{}]'.format(match.group(1))

                    else:
                        app_name = windows[winID]['class'].lower().strip()

                    if app_name:
                        apps.add(app_name)

                except KeyError:
                    print('Missing window (ID={})'.format(winID))

            tags.append('{} {}{}{} {}'.format(
                colors(fg_selected, bg_selected) if tag_status == '#'
                    else colors(fg_normal, bg_normal) if tag_status == ':'
                    else colors(fg_urgent, bg_urgent) if tag_status == '!'
                    else colors(fg_fade, bg_fade),
                name,
                ':' if len(apps) else '',
                '+'.join(sorted(apps)),
                colors(fg_normal, bg_normal)
            ))

        padding = panel_width - text_width(status)
        dzen2_src = '{}^pa({}){}\n'.format(''.join(tags), padding, status).encode()

        dzen2.stdin.write(dzen2_src)
        dzen2.stdin.flush()
