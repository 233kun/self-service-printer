import os

from fastapi import APIRouter
from starlette.responses import FileResponse

from print_queue import get_task

router = APIRouter()


@router.get("/queue/get_job")
def get_queue():
    try:
        get_task(0)
    except:
        print("task is empty")
    else:
        return {"message": get_task(0)}
