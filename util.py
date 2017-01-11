from subprocess import check_output, Popen, PIPE

def cmd(*cmds):
    return check_output(list(cmds)).strip().decode()

def shell_cmd(cmd):
    return check_output(cmd, shell=True).strip().decode()

def hc(*cmds):
    return check_output(['herbstclient'] + list(cmds)).strip().decode()

def colors(fg, bg):
    return '^fg({})^bg({})'.format(fg, bg)
