import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi_utilities import repeat_every
from starlette.middleware.cors import CORSMiddleware

import global_var
from global_vars import bills_global_var, files_attributes_global_var
import print_queue
from routers import user, printer
from routers import pay
import global_vars
from files_dump import dump_queue_files, dump_save_files, startup

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


bills_global_var.init()
files_attributes_global_var.init()
files_attributes_global_var.setter(1234, "asdasda")




@app.get("/")
async def root():
    pass
    # return JSONResponse(status_code=503, content={"message": "Item not found"})


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
