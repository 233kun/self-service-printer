import http.client
import json
import urllib.request
from json import JSONDecodeError
from ssl import SSLEOFError


def get_jobs_tickets():
    connection = http.client.HTTPSConnection("47.106.100.54:8000", timeout=5)
    try:
        connection.request("GET", "/printer/get_job")
        job_response = connection.getresponse().read().decode("UTF-8")
        print_ticket = json.loads(job_response)
    except JSONDecodeError as e:
        print(e)
        return {"message": "jobs not found"}
    except SSLEOFError as e:
        print(e)
        return {"message": "jobs not found"}
    except Exception as e:
        print(e)
        return {"message": "jobs not found"}
    return print_ticket
