from datetime import datetime

import jwt
from models import GlobalVar


def init():
    global expiry
    expiry = GlobalVar()


def setter(key, value):
    expiry.setter(key, value)


def getter(key):
    return expiry.getter(key)


def free(key):
    expiry.free(key)


def renew_expire(directory):
    expire_time = datetime.now().timestamp() + 60 * 15
    setter(directory, expire_time)
