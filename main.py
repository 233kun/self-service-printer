import uvicorn
from fastapi import FastAPI, UploadFile, Request
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routers import user
import jwt

app = FastAPI()
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    # return {"message": jwt.verify_token()}
    # return {"message": jwt.create_token()}
    return {"message": jwt.renew_token()}


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
