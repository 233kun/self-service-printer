import datetime
import http.client
import json
from time import sleep

from download_files import download_files
from get_jobs import get_jobs_tickets
from handle_jobs import handle_jobs
from jobs_monitor import jobs_monitor

previous_ticket = None
retry_counter = 0
if __name__ == '__main__':
    while True:
        sleep(1)
        job_id = 0
        monitor_counter = 0

        job_ticket = get_jobs_tickets()
        if job_ticket.get("message") == "jobs found":
            print("Jobs found")
            print(job_ticket)
        if not retry_counter < 10 and job_ticket.get("message") == "jobs found":
            try:
                while True:
                    json_body = {'file': job_ticket.get('file'), 'out_trade_no': job_ticket.get('out_trade_no')}
                    params = json.dumps(json_body)
                    headers = {"Content-type": "application/json",
                               "accept": "application/json"}
                    connection = http.client.HTTPSConnection("47.106.100.54:8000", timeout=5)
                    connection.request("POST", "/printer/update/job_states", params, headers)
                    break
            except Exception as e:
                print("Error while update job states")
                print(e)
        if job_ticket.get("message") == "jobs found" and job_ticket == previous_ticket:
            retry_counter = retry_counter + 1
            continue
        previous_ticket = job_ticket
        if job_ticket.get("message") == "jobs not found":
            continue
        if not job_ticket.get("message") == "jobs found":
            continue
        if not download_files(job_ticket):
            continue
        job_id = handle_jobs(job_ticket)
        while True:
            sleep(1)
            job_pages = int(job_ticket.get("ranges").split('-')[1]) - int(job_ticket.get("ranges").split('-')[0]) + 1
            if jobs_monitor(job_id):  # check printer is finishing
                print("monitor")
                json_body = {'file': job_ticket.get('file'), 'out_trade_no': job_ticket.get('out_trade_no')}
                params = json.dumps(json_body)
                headers = {"Content-type": "application/json",
                           "accept": "application/json"}
                for index in range(10):  # time out retry
                    try:
                        connection = http.client.HTTPSConnection("47.106.100.54:8000", timeout=5)
                        connection.request("POST", "/printer/update/job_states", params, headers)
                        break
                    except Exception as e:
                        print("Error while update job states")
                        print(e)
                break
            if not monitor_counter < job_pages * 10 + 30:
                break
            monitor_counter = monitor_counter + 1
