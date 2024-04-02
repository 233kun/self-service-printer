import os
from datetime import datetime, time
from time import sleep

from global_var import global_var_getter, free_var


def startup():
    directory = "save_files"
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    directory = "print_queue"
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def dump_save_files():
    # print(datetime.now())
    directories = os.listdir("save_files")
    for directory in directories:

        if int(global_var_getter(f"{directory}_expire")) < datetime.now().timestamp():
            files = os.listdir(f"save_files/{directory}/raw")
            for file in files:
                free_var(directory + file)
            free_var(f"{directory}_expire")

            for root, dirs, files in os.walk(f"save_files/{directory}", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(f"save_files/{directory}")


def dump_queue_files():
    directories = os.listdir("print_queue")
    for directory in directories:
        if int(global_var_getter(f"{directory}_expire")) < datetime.now().timestamp():
            free_var(f"{directory}_expire")
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        os.rmdir(f"save_files/{directory}")
