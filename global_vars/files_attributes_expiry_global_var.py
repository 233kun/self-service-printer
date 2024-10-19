from models import GlobalVar


def init():
    global files_attributes_expiry
    files_attributes_expiry = GlobalVar()


def setter(key, value):
    files_attributes_expiry.setter(key, value)


def getter(key):
    return files_attributes_expiry.getter(key)


def free(key):
    files_attributes_expiry.free(key)
