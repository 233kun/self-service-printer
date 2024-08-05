import asyncio
from contextlib import asynccontextmanager
from datetime import time

import uvicorn
from fastapi import FastAPI, UploadFile, Request, BackgroundTasks
from fastapi_utilities import repeat_every
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import FileResponse, HTMLResponse, JSONResponse

import bills_global_var
import global_test
import models
import print_queue
from routers import user, printer
from routers import pay
import jwt
from convert import convert_docs
import global_var
from files_dump import dump_queue_files, dump_save_files, startup
import time

app = FastAPI()
app.include_router(user.router)
app.include_router(pay.router)
app.include_router(printer.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
global_var.init()  # init in main function
print_queue.init()
global_var.global_var_setter("status", "")
global_var.global_var_setter("printer_status", "running")

global_test.init()
global_test.setter('1', 1)
bills_global_var.init()
bills_global_var.init()




@app.get("/")
async def root():
    print('start job')
    return models.FileBill()
    # return JSONResponse(status_code=503, content={"message": "Item not found"})


@app.get("/status")
async def status():
    return {"message": global_var.global_var_getter("status")}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# @app.post("/uploadfile")
# async def create_upload_file(file: UploadFile, request: Request):
#     with open(f'save_files//{file.filename}', "wb") as f:
#         f.write(file.file.read())
#     print(request.headers.get("token"))
#     return {"filename": file.filename}
async def print_hello():
    print("hello")
    await asyncio.sleep(5)
    print("world")


async def dump_files_loop():
    dump_save_files()
    dump_queue_files()


@app.on_event('startup')
# async def startup_event():
#     asyncio.create_task(dump_files_loop())
@repeat_every(seconds=3)
async def print_hello():
    dump_save_files()
    dump_queue_files()


if __name__ == "__main__":
    startup()
    uvicorn.run(app, host="127.0.0.1", port=8000)
