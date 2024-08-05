from models import GlobalVar


def init():
    global convert_status_vars
    convert_status_vars = GlobalVar()


def setter(key, value):
    convert_status_vars.setter(key, value)


def getter(key):
    return convert_status_vars.getter(key)


def free(key):
    convert_status_vars.free(key)
