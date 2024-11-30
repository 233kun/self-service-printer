from models import GlobalVar


def init():
    global files_attributes_vars
    files_attributes_vars = GlobalVar()


def setter(key, value):
    files_attributes_vars.setter(key, value)


def getter(key):
    return files_attributes_vars.getter(key)


def free(key):
    files_attributes_vars.free(key)
