import uvicorn
from fastapi import FastAPI, UploadFile, Request
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routers import user
import jwt
from doc_convert import doc_convert
import global_var

app = FastAPI()
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_var.init()  # init in main function
global_var.global_var_setter("status", "")


@app.get("/")
async def root():
    return {"message": {"a": 1,"b": 1}}


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
    uvicorn.run(app, host="127.0.0.1", port=8000)
