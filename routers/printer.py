from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse

import global_var
from models import ReturnResult
from print_queue import get_job, get_queue_size, queue_pop

router = APIRouter()


@router.get("/printer/get_job")
def printer_get_job():
    if get_queue_size() == 0:
        return ReturnResult(200, "success", {'jobs': []})
    if get_queue_size() > 0:
        bill_attributes = get_job(0)
        return ReturnResult(200, "success", {'jobs': bill_attributes.get('files_attributes')})


@router.get("/printer/get_file")
def get_file(out_trade_no: str, file: str):
    return FileResponse(f"print_queue/{out_trade_no}/{file}")


class UpdateJob(BaseModel):
    file: str
    out_trade_no: str


class UpdateState(BaseModel):
    state: str


@router.post("/printer/update/job_states")
def update_job_status(updateJob: UpdateJob):
    queue_size = get_queue_size()
    print(get_queue_size())
    for index in range(queue_size):
        if get_job(index).get("file") == updateJob.file:
            if get_job(index).get("out_trade_no") == updateJob.out_trade_no:
                queue_pop(index)
                return {"message": "success"}
    return {"message": "fail"}


@router.get("/printer/status")
def get_printer_status():
    return global_var.global_var_getter("printer_status")


@router.post("/printer/update/status")
def update_printer_status(updateState: UpdateState):
    global_var.global_var_setter("printer_status", updateState.state)
    return {"message": "success"}
