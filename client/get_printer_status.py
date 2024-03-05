import subprocess
import urllib
import http.client
from global_var import global_var_setter, global_var_getter


def get_printer_status():
    output = subprocess.run(
        "ipptool -tv http://192.168.123.139:631/printers/HP_LaserJet_P2015_Series '/root/status.ipp'",
        capture_output=True,
        shell=True,
        text=True)
    print(output.stdout.split("\n")[23])

    try:
        global_var_getter("watch_printer_status_times")
    except:
        global_var_setter("watch_printer_status_times", 0)
    if output.stdout.split("\n")[23] == "processing":
        watch_times = 0
        watch_times = global_var_getter("watch_printer_status_times")
        global_var_setter("watch_printer_status_times", watch_times + 1)
    global_var_setter("watch_printer_status_times", 0)

    status = ""
    if global_var_getter("watch_printer_status_times") <= 6:
        status = "normal"
    elif global_var_getter("watch_printer_status_times") <= 12:
        status = "busy"
    else:
        status = "warning"
    params = urllib.parse.urlencode({"status": status})
    headers = {'accept': 'application/json'}
    connection = http.client.HTTPConnection("127.0.0.1:8000/")
    connection.request("POST", "", params, headers)
    connection.close()
