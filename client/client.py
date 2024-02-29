from cron import loop_function
from  get_printer_status import get_printer_status
if __name__ == '__main__':
    loop_function(get_printer_status(), 5)