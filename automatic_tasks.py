import asyncio
import json
import os
from datetime import datetime, time
from global_vars import expire_global_var, files_attributes_global_var
from global_vars import bills_global_var


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


def clear_expired_directories():
    directories = os.listdir("uploads")
    for directory in directories:
        if expire_global_var.getter(directory) < datetime.now().timestamp():
            try:
                files_attributes_global_var.free(directory)
            except Exception as e:
                pass
            expire_global_var.free(directory)

            for root, dirs, files in os.walk(f"uploads/{directory}", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(f"uploads/{directory}")


def clear_expired_bills():
    bills = bills_global_var.getAll()
    for key in bills.copy():
        if bills.get(key).get('expiry') < datetime.now().timestamp():
            bills_global_var.free(key)
