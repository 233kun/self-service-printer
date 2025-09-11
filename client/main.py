import http.client
import json
import logging
import os.path
import subprocess
import urllib.request
from time import sleep, time
from urllib.parse import quote
SERVER_HOST = '47.106.100.54:8000'
PRINTER_URL = 'http://192.168.123.138:631/printers/HP_LaserJet_P2015_Series'
SECRET_KEY = '123456789'
PRINTING_TIMEOUT_PRE_PAGE = 10
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger()

def polling_jobs(interval):
    while True:
        sleep(interval)

        connection = http.client.HTTPSConnection(SERVER_HOST, timeout=5)
        connection.request('GET', '/printer/jobs')
        response_body = connection.getresponse().read().decode("UTF-8")
        connection.close()

        response_dict = json.loads(response_body)
        if response_dict.get('data').get('jobs') is None:
            continue
        logging.info(f'Received response from server: Response = {response_body}')

        job_attrs = response_dict.get('data').get('jobs')
        path = job_attrs.get('folder')
        filename = job_attrs.get('filename')
        filename_pdf = filename.rsplit('.', 1)[0] + '.pdf'
        try:
            response = urllib.request.urlopen(f"https://{SERVER_HOST}/printer/file?path={path}&filename={quote(filename_pdf)}", timeout=5)
        except Exception as e:
            logger.error(e)
        else:
            json_body = {'filename': job_attrs.get('filename'),
                         'folder': job_attrs.get('folder'),
                         'state': 'success',
                         'authentication': SECRET_KEY}
            params = json.dumps(json_body)
            headers = {"Content-type": "application/json",
                       "accept": "application/json"}
            connection = http.client.HTTPSConnection(SERVER_HOST, timeout=5)
            connection.request('POST', '/printer/job/state', params, headers)
        if not os.path.exists(f'downloads/{path}/'):
            os.mkdir(f'downloads/{path}')
        with open(f"downloads/{path}/{filename_pdf}", 'wb') as f:
            f.write(response.read())
        return job_attrs


def execute_ipptool(job_attributes):
    print_copies = job_attributes.get('print_copies')
    print_range_start = job_attributes.get('print_range_start')
    print_range_end = job_attributes.get('print_range_end')
    print_ranges = str(print_range_start) + '-' + str(print_range_end)
    print_file_path = job_attributes.get('folder')
    print_filename = job_attributes.get('filename').rsplit('.', 1)[0] + '.pdf'
    print_side = job_attributes.get('print_side')
    if print_side == 'one-sided':
        print_side = 'one-sided'
    elif print_side == 'two-sided-default':
        print_side = 'two-sided-long-edge'
    elif print_side == 'two-sided-long-edge':
        print_side = 'two-sided-long-edge'
    elif print_side == 'two-sided-short-edge':
        print_side = 'two-sided-short-edge'
    ipp_file_path = os.path.abspath("ipp_files/print_ticket_attributes.ipp")
    submit_print_job = subprocess.run(
        f"ipptool -tv {PRINTER_URL} -f "
        f"'downloads/{print_file_path}/{print_filename}' -d sides={print_side} -d page-ranges={print_ranges} -d "
        f"copies={print_copies} {ipp_file_path}",
        capture_output=True,
        shell=True,
        text=True)
    if submit_print_job.stdout == '':
        raise '[ERROR] Fail to execute job'
    job_id = submit_print_job.stdout.split("\n")[14][27:]
    return job_id


def poll_cups_job_state(job_id, job_attributes, timeout, interval=5):
    start_time = time()
    while True:
        ipp_file_path = os.path.abspath("ipp_files/job_attributes.ipp")
        job_state = subprocess.run(
            f"ipptool -tv {PRINTER_URL} -d job-id={job_id} {ipp_file_path}",
            capture_output=True,
            shell=True,
            text=True)
        if job_state.stdout == '':
            raise '[ERROR] Fail to get job state'
        start = job_state.stdout.find("job-state (enum) = ")
        end = job_state.stdout.find("\n", start)
        job_state = job_state.stdout[start + 19:end]
        if job_state == "completed":
            print_filename = job_attributes.get('filename').rsplit('.', 1)[0] + '.pdf'
            if os.path.exists(f'downloads/{print_filename}'):
                os.remove(f'downloads/{print_filename}')
            return 'success'
        if time() - start_time > timeout:
            return 'error'
        sleep(interval)


if __name__ == '__main__':
    while True:
        try:
            job_attributes = polling_jobs(interval=1)
            job_id = execute_ipptool(job_attributes)
            job_state = poll_cups_job_state(job_id, job_attributes, timeout=job_attributes.get('total_pages') * 10)
        except Exception as e:
            logger.error(e)
            continue

        try:
            if job_state == 'error':
                json_body = {'filename': job_attributes.get('filename'),
                             'folder': job_attributes.get('folder')}
                params = json.dumps(json_body)
                headers = {"Content-type": "application/json",
                           "accept": "application/json"}
                connection = http.client.HTTPSConnection("SERVER_HOST", timeout=5)
                # connection.request('POST', '/printer/job/state')
                # 等未来做好商家端的时候添加异常文件上报
        except Exception as e:
            logger.error(e)

