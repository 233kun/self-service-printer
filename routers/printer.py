import json
import os
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import Json, BaseModel
from starlette.responses import FileResponse
from typing_extensions import Annotated

import global_var
from print_queue import get_job, queue_remove, get_queue_size, queue_pop

router = APIRouter()


@router.get("/printer/get_job")
def printer_get_job():
    try:
        get_job(0)
    except BaseException:
        return {"message": "no jobs found"}
    else:
        return {"message": "jobs found",
                "file": get_job(0).get("file"),
                "out_trade_no": get_job(0).get("out_trade_no"),
                "sides": get_job(0).get("sides"),
                "ranges": get_job(0).get("ranges"),
                "copies": get_job(0).get("copies")
                }


@router.get("/printer/get_file")
def get_file(out_trade_no: str, file: str):
    return FileResponse(f"print_queue/{out_trade_no}/{file}")

    # try:
    #     task_index = 0
    #     while True:
    #         if not global_var.global_var_getter(get_task(task_index)):
    #             raise HTTPException(status_code=404, detail="404 not found")
    #         files = os.listdir(f"print_queue/get_task(task_index)")
    #         for file in files:
    #             return FileResponse(f"print_queue/get_task(task_index)")
    #             break

    # except:
    #     print("task is empty")


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
