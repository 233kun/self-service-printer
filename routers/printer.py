import os

from fastapi import APIRouter, HTTPException
from pydantic import Json
from starlette.responses import FileResponse
from typing_extensions import Annotated

import global_var
from print_queue import get_task

router = APIRouter()


@router.get("/queue/get_job")
def get_queue():
    try:
        task_index = 0
        while True:
            if not global_var.global_var_getter(get_task(task_index)):
                raise HTTPException(status_code=404, detail="404 not found")
            files = os.listdir(f"print_queue/get_task(task_index)")
            for file in files:
                return FileResponse(f"print_queue/get_task(task_index)")
                break


    except:
        print("task is empty")


@router.get("/printer/status")
def get_printer_status():
    return global_var.global_var_setter("printer_status")


@router.post("/printer/update_status")
def update_printer_status(status: Annotated[str, Json()]):
    global_var.global_var_setter("printer_status", status)
    return {"message": "success"}
