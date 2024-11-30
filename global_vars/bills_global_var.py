from models import GlobalVar


def init():
    global bill_vars
    bill_vars = GlobalVar()


def setter(key, value):
    bill_vars.setter(key, value)


def getter(key):
    return bill_vars.getter(key)


def getAll():
    return bill_vars.getAll()


def free(key):
    bill_vars.free(key)
