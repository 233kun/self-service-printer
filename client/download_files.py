import os
import urllib.request
from urllib.parse import quote


def download_files(print_ticket: dict):
    global response
    try:
        response = urllib.request.urlopen(f"https://47.106.100.54:8000/printer/get_file?out_trade_no="
                                          f"{print_ticket.get('out_trade_no')}&file={quote(print_ticket.get('file'))}",
                                          timeout=5)
    except Exception as e:
        print(e)
    if not os.path.exists(f"save_files/{print_ticket.get('out_trade_no')}"):
        os.mkdir(f"save_files/{print_ticket.get('out_trade_no')}")
    with open(f"save_files/{print_ticket.get('out_trade_no')}/{print_ticket.get('file')}", 'wb') as f:
        f.write(response.read())