import os
from datetime import datetime

from global_var import global_var_getter, free_var


async def dump_save_files():
    directories = os.listdir("save_files")
    for directory in directories:
        if global_var_getter(f"{directory}_expire") < datetime.now():
            os.remove(f"save_files/{directory}")
            free_var(f"{directory}_expire")


async def dump_queue_files():
    directories = os.listdir("save_files/print_queue")
    for directory in directories:
        if global_var_getter(f"{directory}_expire") < datetime.now():
            os.remove(f"save_files/print_queue/{directory}")
            free_var(f"{directory}_expire")
