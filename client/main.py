import os
import json
import logging
import subprocess
import urllib.request
from time import sleep
from urllib.parse import quote

import setting

logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO，会记录INFO及以上级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_new_job():
    try:
        req = urllib.request.Request(f"{setting.SERVER_HOST}/printer/jobs")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {setting.SECRET_KEY}")
        res = urllib.request.urlopen(req)

        job_attributes = json.loads(res.read().decode("utf-8")).get("data").get("jobs")
        if job_attributes is None:
            return None
        return job_attributes
    except urllib.request.HTTPError as e:
        logging.error("Network Error: Unable to connect to server")
        logging.error(e)
    except json.decoder.JSONDecodeError as e:
        logging.error("JSON Decode Error: Failed to decode JSON")
        logging.error(e)
    except Exception as e:
        logging.error("Unexpected error occurred")
        logging.error(e)


def download_job_file(job_attributes):
    folder = job_attributes.get("folder")
    filename = job_attributes.get("filename")
    try:
        req = urllib.request.Request(
            f"{setting.SERVER_HOST}/printer/file?path={folder}&filename={quote(filename)}"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {setting.SECRET_KEY}")
        res = urllib.request.urlopen(req)

        if not os.path.exists(f"downloads/{folder}"):
            os.mkdir(f"downloads/{folder}")
        with open(f"downloads/{folder}/{filename}", "wb") as f:
            f.write(res.read())
        params_body = {
            "filename": filename,
            "folder": folder,
            "state": "success",
            "authentication": setting.SECRET_KEY,
        }
        params = json.dumps(params_body).encode("utf-8")
        req = urllib.request.Request(f"{setting.SERVER_HOST}/printer/job/state", params)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {setting.SECRET_KEY}")
        res = urllib.request.urlopen(req)
        return f"{folder}/{filename}"
    except urllib.request.HTTPError as e:
        logging.error("Network Error: Unable to connect to server")
        logging.error(e)
    except Exception as e:
        logging.error("Unexpected error occurred")
        logging.error(e)


def exec_printing_linux(job_attributes):
    print_copies = job_attributes.get("print_copies")
    print_range_start = job_attributes.get("print_range_start")
    print_range_end = job_attributes.get("print_range_end")
    print_range = str(print_range_start) + "-" + str(print_range_end)
    print_side = job_attributes.get("print_side")
    folder = job_attributes.get("folder")
    filename = job_attributes.get("filename")

    if print_side == 'one-sided':
        print_side = 'one-sided'
    elif print_side == 'two-sided-default':
        print_side = 'two-sided-long-edge'
    elif print_side == 'two-sided-long-edge':
        print_side = 'two-sided-long-edge'
    elif print_side == 'two-sided-short-edge':
        print_side = 'two-sided-short-edge'
    try:
        exec_print = subprocess.run(
            [
                "ipptool", "-tv", setting.PRINTER_URL, "-f", f"downloads/{folder}/{filename}", "-d", f"sides={print_side}", "-d", f"page-ranges={print_range}", "-d", f"copies={print_copies}", "ipp_files/print_ticket_attributes.ipp"
            ],
        capture_output=True,
        text=True
        )
        if exec_print.returncode == 0:
            if exec_print.stdout.find("job-id") == -1:
                logging.error("Print Error: Failed to print job, job_attributes:")
                logging.error(job_attributes)
                logging.error("stout:")
                logging.error(exec_print.stdout)
            else:
                if os.path.exists(f"downloads/{folder}/{filename}"):
                    os.remove(f"downloads/{folder}/{filename}")
                    if len(os.listdir(f"downloads/{folder}")) == 0:
                        os.remove(f"downloads/{folder}")
                logging.info("Success print, job_attributes:")
                print(job_attributes)
        else:
            logging.error("Print Error: Failed to print job, job_attributes:")
            print(job_attributes)
            logging.error("stderr:")
            print(exec_print.stderr)
    except Exception as e:
        print(exec_print.args)
        logging.error("Unexpected error occurred")
        logging.error(e)
        return None

if __name__ == "__main__":
    while True:
        sleep(1)
        job_attributes = get_new_job()
        if job_attributes is None:
            continue

        file_path = download_job_file(job_attributes)
        if file_path is None:
            continue

        exec = exec_printing_linux(job_attributes)
