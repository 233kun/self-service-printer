import json
import os

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse

import global_var
from models import ReturnResult, UpdateJob, UpdateState
from print_queue import get_job, get_queue_size, queue_pop
from setting import SECRET_KEY

router = APIRouter()


@router.get("/printer/jobs")
def printer_get_job():
    if get_queue_size() == 0:
        return ReturnResult(200, "success", {'jobs': {}})
    if get_queue_size() > 0:
        job_attributes = get_job(0)
        return ReturnResult(200, "success", {'jobs': job_attributes})


@router.get("/printer/file")
def get_file(path: str, filename: str):
    return FileResponse(f"pending_files/{path}/{filename}")


@router.post("/printer/job/state")
def update_job_status(update_state: UpdateState):
    if not update_state.authorization == SECRET_KEY:
        return ReturnResult(200, 'authorization error')
    queue_size = get_queue_size()
    for index in range(queue_size):
        job_attributes = get_job(index)
        folder = job_attributes.get('folder')
        filename = job_attributes.get('filename')
        if filename != update_state.filename:
            continue
        if folder != update_state.path:
            continue
        queue_pop(index)
        filename_pdf = filename.rsplit('.', 1)[0] + '.pdf'
        os.remove(f'pending_files/{folder}/{filename_pdf}')
        if os.listdir(f'pending_files/{folder}/') == []:
            os.rmdir(f'pending_files/{folder}')
        break
    return ReturnResult(200, "success", {})
