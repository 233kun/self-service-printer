import os.path
from imp import reload
from os import mkdir
from typing import Annotated
from urllib.request import Request
from fastapi import APIRouter, UploadFile, Header
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from globle_var import init_globle_var
import jwt

router = APIRouter()


@router.post("/test/")
async def test(file: UploadFile):
    return {"filename": file.filename}


@router.get("/token/get")
async def get_token():
    return {"token": jwt.create_token()}


class JwtToken(BaseModel):
    token: object


@router.post("/token/renew")
async def renew_token(jwtToken: JwtToken):
    return {"token": jwt.renew_token(jwtToken.token)}
    # return {jwtToken.token}


@router.put("/uploadfile")
async def create_upload_file(file: UploadFile, Authentication: Annotated[str | None, Header()]):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")
    if not os.path.exists("save_files/" + directory):
        mkdir(f"save_files/{directory}")
        mkdir(f"save_files/{directory}/raw")
        mkdir(f"save_files/{directory}/converted")
    with open(f'save_files/{directory}/raw/{file.filename}', "wb") as f:
        f.write(file.file.read())
    with open(f'save_files/{directory}/expire', "wb") as f:
        f.write(str(expire).encode())
    return {"message": "success"}


@router.get("/uploadfile/filelist")
async def get_folder(Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        expire = payload.get("exp")
        if not os.path.exists("save_files/" + directory):
            mkdir(f"save_files/{directory}")
            mkdir(f"save_files/{directory}/raw")
            mkdir(f"save_files/{directory}/converted")
            with open(f'save_files/{directory}/expire', "wb") as f:
                f.write(str(expire).encode())
        files = os.listdir(f"save_files/{directory}/raw")
        return {"message": files}
    else:
        return {"message": "fail"}


class FileToRemove(BaseModel):
    filename: str


@router.post("/uploadfile/remove")
async def create_item(fileToRemove: FileToRemove, Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        os.remove(f"save_files/{directory}/raw/{fileToRemove.filename}")
        return {"message": "success"}
    else:
        return {"message": "fail"}
    # return {"message": fileToRemove.filename, "token": Authentication}
