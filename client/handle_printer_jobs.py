import http.client
import json
import os
import subprocess
import urllib.request
import urllib.parse
from json import JSONDecodeError
from ssl import SSLEOFError
from urllib.parse import quote
from datetime import datetime
from time import sleep

import global_var


def handle_printer_jobs():
    connection = http.client.HTTPSConnection("47.106.100.54:8000", timeout=5)
    try:
        connection.request("GET", "/printer/get_job")
        job_response = connection.getresponse().read().decode("UTF-8")
        print_ticket = json.loads(job_response)
    except JSONDecodeError:
        print("response body decode error")
        return
    except SSLEOFError:
        print("connection error")
        return
    if not print_ticket.get("message") == "jobs found":
        return
    try:
        response = urllib.request.urlopen(f"https://47.106.100.54:8000/printer/get_file?out_trade_no="
                                          f"{print_ticket.get('out_trade_no')}&file={quote(print_ticket.get('file'))}",
                                          timeout=5)
    except:
        print("download file error")
        return
    if not os.path.exists(f"save_files/{print_ticket.get('out_trade_no')}"):
        os.mkdir(f"save_files/{print_ticket.get('out_trade_no')}")
    with open(f"save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')}", 'wb') as f:
        f.write(response.read())

    global_var.global_var_setter(f"{print_ticket.get('out_trade_no')}_expire", datetime.now().timestamp() + 60 * 15)
    sides = ""
    if print_ticket.get("sides"):
        sides = "two-sided-long-edge"
    else:
        sides = "one-sided"
    submit_print_job = subprocess.run(
        f"ipptool -tv http://192.168.123.139:631/printers/HP_LaserJet_P2015_Series -f 'save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')}' -d sides={sides} -d page-ranges={print_ticket.get('ranges')} -d copies={print_ticket.get('copies')} print_ticket_attributes.ipp",
        capture_output=True,
        shell=True,
        text=True)
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
        total_pages = int(print_ticket.get("ranges").split('-')[1]) - int(print_ticket.get("ranges").split('-')[0])
        if total_pages * 10 + 30 < monitor_times:
            params = urllib.parse.urlencode({'@state': "error"})
            headers = {"Content-type": "application/json",
                       "accept": "application/json"}
            connection.request("post", "/printer/update/status", params, headers)
            print('printer error')
            exit()

        if job_state[0:9] == "completed":
            print(print_ticket.get('file'))
            print(print_ticket.get('out_trade_no'))
            # params = urllib.parse.urlencode({'@file': print_ticket.get('file'), '@out_trade_no': print_ticket.get('out_trade_no')})
            json_body = {'file': print_ticket.get('file'), 'out_trade_no': print_ticket.get('out_trade_no')}
            params = json.dumps(json_body)
            print(json_body)
            headers = {"Content-type": "application/json",
                       "accept": "application/json"}
            while True:  # time out retry
                try:
                    connection.request("POST", "/printer/update/job_states", params, headers)
                    break
                except:
                    print("update job states fail")
            if connection.getresponse().read().decode("UTF-8") == '{"message":"success"}':
                break  # The end of Looping
        print(monitor_times)
        sleep(1)


if __name__ == "__main__":
    handle_printer_jobs()
