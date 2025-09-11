import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.responses import FileResponse

from jwt import security
from models import ReturnResult, UpdateJob, UpdateState
from print_queue import print_queue_singleton
from setting import SECRET_KEY

router = APIRouter()

def verify_secret_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    secret_key = credentials.credentials
    if secret_key == SECRET_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail="Invalid secret key",
    )
    return False

@router.get("/printer/jobs")
def printer_get_job(bool = Depends(verify_secret_key)):
    print_queue = print_queue_singleton().data
    if len(print_queue) == 0:
        return ReturnResult(200, 'success', {'jobs': None})
    return ReturnResult(200, 'success', {'jobs': print_queue[0]})


@router.get("/printer/file")
def get_file(path: str, filename: str, bool = Depends(verify_secret_key)):
    return FileResponse(f"pending_files/{path}/{filename}")


@router.post("/printer/job/state")
def update_job_status(update_state: UpdateState, bool = Depends(verify_secret_key)):
    if not update_state.authentication == SECRET_KEY:
        return ReturnResult(200, 'authorization error', {})
    print_queue = print_queue_singleton().data
    for index in range(len(print_queue)):
        job_attributes = print_queue[index]
        folder = job_attributes.get('folder')
        filename = job_attributes.get('filename')
        if filename != update_state.filename:
            continue
        if folder != update_state.folder:
            continue
        print_queue.pop(index - 1)
        filename_pdf = filename.rsplit('.', 1)[0] + '.pdf'
        os.remove(f'pending_files/{folder}/{filename_pdf}')
        if os.listdir(f'pending_files/{folder}/') == []:
            os.rmdir(f'pending_files/{folder}')
    return ReturnResult(200, "success", {})