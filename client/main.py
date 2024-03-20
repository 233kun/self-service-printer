from datetime import datetime

import global_var
from handle_printer_jobs import handle_printer_jobs
from time import sleep

if __name__ == '__main__':
    global_var.init()
    while True:
        try:
            handle_printer_jobs()
        except:
            pass
            print("job exception")
        sleep(1)
        print(datetime.now())
