import models


def init():
    global _global_var
    _global_var = models.GlobalVar()


def setter(key, value):
    _global_var.setter(key, value)


def getter(key):
    return _global_var.getter(key)

