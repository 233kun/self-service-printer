import http.client
import json
import os
import subprocess
import urllib.request
import urllib.parse
from urllib.parse import quote
from datetime import datetime
from time import sleep

import global_var


def handle_printer_jobs():
    connection = http.client.HTTPConnection("47.106.100.54:8000")
    connection.request("GET", "/printer/get_job")
    job_response = connection.getresponse().read().decode("utf-8")
    print_ticket = json.loads(job_response)
    if print_ticket.get("message") == "no jobs found":
        return
    response = urllib.request.urlopen(f"http://47.106.100.54:8000/printer/get_job?out_trade_no="
                                      f"{print_ticket.get('out_trade_no')}&file={quote(print_ticket.get('file'))}")
    if not os.path.exists(f"save_files/{print_ticket.get('out_trade_no')}"):
        os.mkdir(f"save_files/{print_ticket.get('out_trade_no')}")
    with open(f"save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')}", 'wb') as f:
        f.write(response.read())
    global_var.global_var_setter(f"{print_ticket.get('out_trade_no')}_expire", datetime.now().timestamp() + 60 * 15)

    sides = ""
    if print_ticket.get("sides"):
        sides = "one-sided"
    else:
        sides = "two-sided-long-edge"
    submit_print_job = subprocess.run(
        f"ipptool -tv http://192.168.123.139:631/printers/HP_LaserJet_P2015_Series -f 'save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')}' -d sides={sides} -d page-ranges={print_ticket.get('ranges')} -d copies={print_ticket.get('copies')} print_tic<nt_ticket_attributes.ipp",
        capture_output=True,
        shell=True,
        text=True)
    print(f"save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')} -d sides={sides} -d page-ranges={print_ticket.get('ranges')} -d copies=1 ")
    print(submit_print_job.stdout)
    job_id = submit_print_job.stdout.split("\n")[14][27:]
    monitor_times = 0
    previous_job_state = ""
    # print_total_pages = (print_ticket.get("ranges").split("-")[1] - print_ticket.get("ranges").split("-")[0]) * print_ticket.get("copies")
    while True:
        get_job_attributes = subprocess.run(
            f"ipptool -tv http://192.168.123.139:631/printers/HP_LaserJet_P2015_Series -d job-id={job_id} job_attributes.ipp",
        capture_output=True,
        shell=True,
        text=True)
        start = get_job_attributes.stdout.find("job-state (enum) = ")
        end = get_job_attributes.stdout.find("\n", start)
        job_state = get_job_attributes.stdout[start + 19:end]
        if job_state == previous_job_state:
            monitor_times = monitor_times + 1
        else:
            monitor_times = 0
        previous_job_state = job_state
        if 30 < monitor_times:
            params = urllib.parse.urlencode({'@state': "error"})
            headers = {"Content-type": "application/json",
                       "accept": "application/json"}
            connection.request("post", "/printer/update/status", params, headers)
            print('printer error')
            exit()

        if job_state[0:9] == "completed":
            params = urllib.parse.urlencode({'@file': print_ticket.get('file'), '@out_trade_no': print_ticket.get('out_trade_no')})
            headers = {"Content-type": "application/json",
                       "accept": "application/json"}
            connection.request("post", "/printer/update/job_states", params, headers)
            break
        print(monitor_times)
        sleep(1)


if __name__ == "__main__":
    handle_printer_jobs()
