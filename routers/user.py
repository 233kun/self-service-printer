from os import mkdir

from fastapi import APIRouter, UploadFile
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
    mkdir(f"save_files/{jwtToken}")
    with open(f'save_files/{jwtToken}/{file.filename}', "wb") as f:
        f.write(file.file.read())
    print(jwtToken)
    return {"filename": file.filename}