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


@router.post("/uploadfile/{jwtToken}")
async def create_upload_file(file: UploadFile, jwtToken: str):
    if not jwt.verify_token(jwtToken):
        return {"message": "fail"}
    payload = jwt.decode_token(jwtToken)
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
        print(1)
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        files = os.listdir(f"save_files/{directory}/raw")
        return {"message": files}


