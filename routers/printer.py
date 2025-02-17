import json
import os

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse

import global_var
from models import ReturnResult, UpdateJob, UpdateState
from print_queue import get_job, get_queue_size, queue_pop, print_queue_singleton
from setting import SECRET_KEY

router = APIRouter()


@router.get("/printer/jobs")
def printer_get_job():
    print_queue = print_queue_singleton().data
    if len(print_queue) == 0:
        return ReturnResult(200, 'success', {'jobs': None})
    return ReturnResult(200, 'success', {'jobs': print_queue[0]})


@router.get("/printer/file")
def get_file(path: str, filename: str):
    return FileResponse(f"pending_files/{path}/{filename}")


@router.post("/printer/job/state")
def update_job_status(update_state: UpdateState):
    if not update_state.authorization == SECRET_KEY:
        return ReturnResult(200, 'authorization error')
    print_queue = print_queue_singleton().data
    for index in range(len(print_queue)):
        job_attributes = print_queue[index]
        folder = job_attributes.get('folder')
        filename = job_attributes.get('filename')
        if filename != update_state.filename:
            continue
        if folder != update_state.path:
            continue
        print_queue.pop(index - 1)
        filename_pdf = filename.rsplit('.', 1)[0] + '.pdf'
        os.remove(f'pending_files/{folder}/{filename_pdf}')
        if os.listdir(f'pending_files/{folder}/') == []:
            os.rmdir(f'pending_files/{folder}')
    return ReturnResult(200, "success", {})