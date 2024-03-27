import os
import subprocess


def jobs_monitor(job_id):
    ipp_file_path = os.path.abspath("ipp_files/job_attributes.ipp")
    get_job_attributes = subprocess.run(
        f"ipptool -tv http://192.168.123.139:631/printers/HP_LaserJet_P2015_Series -d job-id={job_id} {ipp_file_path}",
        capture_output=True,
        shell=True,
        text=True)
    start = get_job_attributes.stdout.find("job-state (enum) = ")
    end = get_job_attributes.stdout.find("\n", start)
    # if get_job_attributes.stdout[start + 19:end].find("completed") == -1:
    job_state = get_job_attributes.stdout[start + 19:end]
    if job_state == "completed":
        return True
    else:
        return False
