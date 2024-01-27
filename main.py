import uvicorn
from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    with open(f'save_files/{file.filename}', "wb") as f:
        f.write(file.file.read())
    return {"filename": file.filename}
