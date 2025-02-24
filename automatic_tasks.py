import asyncio
import json
import os
from datetime import datetime, time
from time import sleep

from global_vars.bills_attributes_singleton import bills_attributes_singleton
from global_vars.files_attributes_singleton import files_attributes_singleton


def startup():
    directory = "uploads"
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    directory = "pending_files"
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def clean_expired_directories():
    directories = os.listdir("./uploads")
    for directory in directories:
        with open(f'./uploads/{directory}/expire', "r") as f:
            expire = json.load(f).get('expire')
        if expire < datetime.now().timestamp():
            for root, dirs, files in os.walk(f"./uploads/{directory}", topdown=False):
                for file in files:
                    os.remove(f'{root}/{file}')
                os.rmdir(root)
            files_attributes_global = files_attributes_singleton()
            files_attributes_global.data.pop(directory)


def clear_expired_bills():
    bills_attributes_global = bills_attributes_singleton()
    bills_attributes = bills_attributes_global.data
    for key in bills_attributes:
        if bills_attributes.get(key).get('expiry') < datetime.now().timestamp():
            bills_attributes_global.data.pop(key)
