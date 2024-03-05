import uvicorn
from fastapi import FastAPI, UploadFile, Request
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import FileResponse

import print_queue
from routers import user, printer
from routers import pay
import jwt
from doc_convert import doc_convert
import global_var

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


@app.get("/")
async def root():
    return FileResponse("save_files/9088e7af-b58c-4162-b283-17d8c2d0a3e3/raw/wd-spectools-word-sample-04.doc")


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

if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
