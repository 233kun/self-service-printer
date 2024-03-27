import subprocess


def handle_jobs(print_ticket):
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
    return job_id