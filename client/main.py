from datetime import datetime

import global_var
from handle_printer_jobs import handle_printer_jobs
from time import sleep
if __name__ == '__main__':
    global_var.init()
    while True:
        handle_printer_jobs()
        sleep(1)
        print(datetime.now())