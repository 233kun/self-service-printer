import http.client
import json
import urllib.request
from json import JSONDecodeError
from ssl import SSLEOFError


def get_jobs_tickets():
    try:
        connection = http.client.HTTPSConnection("47.106.100.54:8000", timeout=5)
        connection.request("GET", "/printer/get_job")
        job_response = connection.getresponse().read().decode("UTF-8")
        print_ticket = json.loads(job_response)
        # print("Found job, pending send job to printer")
        # print(print_ticket)
    except Exception as e:
        print("Error while getting job")
        print(e)
        return {"message": "no jobs found"}
    return print_ticket
