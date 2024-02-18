import asyncio
import os.path
import threading
from os import mkdir
from typing import Annotated
from urllib.request import Request
from fastapi import APIRouter, UploadFile, Header, File
from pydantic import BaseModel
from pypdf import PdfReader
from starlette.middleware.cors import CORSMiddleware

import global_var
from doc_convert import doc_convert
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
async def create_upload_file(Authentication: Annotated[str | None, Header()], files: list[UploadFile]):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")
    if not os.path.exists("save_files/" + directory):
        mkdir(f"save_files/{directory}")
        mkdir(f"save_files/{directory}/raw")
        mkdir(f"save_files/{directory}/converted")
    for file in files:
        with open(f'save_files/{directory}/raw/{file.filename}', "wb") as f:
            f.write(file.file.read())
        with open(f'save_files/{directory}/expire', "wb") as f:
            f.write(str(expire).encode())
        global_var.global_var_setter(directory + file.filename, "processing")
    convert_task = threading.Thread(doc_convert(directory))
    convert_task.start()
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
        states = {}
        for file in files:
            page_number = 1
            if global_var.global_var_getter(directory + file) == "success":
                converted_filename = file.rsplit(".", 1)[0] + ".pdf"
                reader = PdfReader(f"save_files/{directory}/converted/{converted_filename}")
                page_number = len(reader.pages)
            states.update(
                {
                    file: {
                        "filename": file,
                        "convert_stata": global_var.global_var_getter(directory + file),
                        # "convert_stata": "error3..",
                        "total_pages": page_number,
                        "print_copies": 1,
                        "print_range_start": 1,
                        "print_range_end": page_number,
                        "print_side": False  # True == single; False == double
                     }
                }
            )
        print(states)
        return {"message": states}
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



