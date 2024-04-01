import asyncio
import os.path
import sys
import threading
from os import mkdir
from shutil import copyfile
from typing import Annotated
from urllib.request import Request

import img2pdf
from fastapi import APIRouter, UploadFile, Header, File
from pydantic import BaseModel
from pypdf import PdfReader
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from global_var import global_var_setter, global_var_getter
from convert import convert_docs, convert_images, convert_excel
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
    for index in range(len(files)):
        filetype = files[index].filename.rsplit(".", 1)[1]
        if filetype == "pdf":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                copyfile(f'save_files/{directory}/raw/{files[index].filename}', f'save_files/{directory}/converted/{file.filename}')
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                return {"message": "success"}

        if filetype == "doc" or filetype == "docx":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
               convert_docs(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                return {"message": "success"}

        if filetype == "xlsx" or filetype == "xls":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                convert_excel(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                return {"message": "success"}

        if filetype == "jpeg" or filetype == "jpg" or filetype == "png":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                convert_images(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                return {"message": "success"}

    return {"message": "error"}


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
            # with open(f'save_files/{directory}/expire', "wb") as f:
            #     f.write(str(expire).encode())
        global_var_setter(f"{directory}_expire", expire)  # free in files_dump.py loop event

        files = os.listdir(f"save_files/{directory}/raw")
        states = {}
        for file in files:
            page_number = 1
            if global_var_getter(directory + file) == "success":
                converted_filename = file.rsplit(".", 1)[0] + ".pdf"
                reader = PdfReader(f"save_files/{directory}/converted/{converted_filename}")
                page_number = len(reader.pages)
            states.update(
                {
                    file: {
                        "filename": file,
                        "convert_state": global_var_getter(directory + file),
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
        converted_filename = fileToRemove.filename.rsplit(".", 1)[0] + ".pdf"
        os.remove(f"save_files/{directory}/raw/{fileToRemove.filename}")
        os.remove(f"save_files/{directory}/converted/{converted_filename}")
        return {"message": "success"}
    else:
        return {"message": "fail"}
    # return {"message": fileToRemove.filename, "token": Authentication}


@router.get("/preview")
async def preview_pdf(filename: str, Authentication: str):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    converted_filename = filename.rsplit(".", 1)[0] + ".pdf"
    return FileResponse(f"save_files/{directory}/converted/{converted_filename}")
