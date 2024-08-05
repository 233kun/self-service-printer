import asyncio
import os.path
import threading
from datetime import time
from os import mkdir
from shutil import copyfile
from typing import Annotated

from fastapi import APIRouter, UploadFile, Header, BackgroundTasks
from pydantic import BaseModel
from pypdf import PdfReader
from starlette.responses import FileResponse

import global_test
import models
from global_var import global_var_setter, global_var_getter
from convert import convert_docs, convert_images, convert_excel
from models import FileModel, ReturnResult
import jwt

router = APIRouter()


@router.get("/token/generation")
async def get_token():
    return ReturnResult(200, "success", {"token": jwt.create_token()})


class JwtToken(BaseModel):
    token: object


@router.post("/token/renew")
async def renew_token(jwtToken: JwtToken):
    return ReturnResult(200, "success", {"token": jwt.renew_token(jwtToken.token.__str__())})


@router.put("/uploadfile")
async def create_upload_file(Authentication: Annotated[str | None, Header()], files: list[UploadFile], background_tasks: BackgroundTasks):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")

    if not os.path.exists("save_files/" + directory):
        mkdir(f"save_files/{directory}")
        mkdir(f"save_files/{directory}/raw")
        mkdir(f"save_files/{directory}/converted")


    files_attributes = []
    for index in range(len(files)):
        with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
            f.write(files[index].file.read())

        file_attributes = FileModel()
        file_attributes.filename = files[index].filename
        file_attributes.convert_state = "processing"
        file_attributes.print_copies = 1
        # file_attribute.print_range_start =
        # file_attribute.print_range_end =
        file_attributes.print_side = "one-sided"

        filename_hash = hash(files[index].filename + directory)

        filetype = files[index].filename.rsplit(".", 1)[1]
        if filetype == "pdf":
            try:
                copyfile(f'save_files/{directory}/raw/{files[index].filename}',
                         f'save_files/{directory}/converted/{files[index].filename}')
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attributes.convert_state = "error"
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attributes.convert_state = "success"

        if filetype == "doc" or filetype == "docx":
            try:
                background_tasks.add_task(convert_docs, convert_docs, files[index].filename, )
            except Exception as e:
                pass
                # print(e)
                # global_var_setter(directory + files[index].filename, "error")
                # file_attributes.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                reader = PdfReader(f"save_files/{directory}/converted/{files[index].filename.rsplit(".", 1)[0]}.pdf")
                file_attributes.total_pages = len(reader.pages)
                file_attributes.print_range_end = len(reader.pages)
                file_attributes.convert_state = "success"

        if filetype == "xlsx" or filetype == "xls":
            try:
                convert_excel(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attributes.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attributes.convert_state = "success"

        if filetype == "jpeg" or filetype == "jpg" or filetype == "png":
            try:
                convert_images(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attributes.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attributes.convert_state = "success"

        files_attributes.append(file_attributes)

    try:
        global_var_getter(directory)
    except BaseException as e:  # when file attributes is empty
        global_var_setter(directory, files_attributes)
    else:  # when file attributes is not empty
        files_attributes_temp = global_var_getter(directory)
        files_attributes_temp = files_attributes_temp + files_attributes
        global_var_setter(directory, files_attributes_temp)
    return ReturnResult(200, "success", files)


@router.get("/uploadfile/filelist")
async def get_folder(Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        expire = payload.get("exp")
        files_attributes = {}
        try:
            files_attributes = global_var_getter(directory)
        except BaseException:
            return ReturnResult(200, "success", {'files_attributes': []})
        else:
            print(ReturnResult(200, "success", {'files_attributes': global_var_getter(directory)}))
            return ReturnResult(200, "success", {'files_attributes': global_var_getter(directory)})


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
        files_attribute = global_var_getter(directory)
        files_attribute.pop(fileToRemove.filename)
        global_var_setter(directory, files_attribute)
        return ReturnResult(200, "success", {})
    else:
        return ReturnResult(200, "error", {})
    # return {"message": fileToRemove.filename, "token": Authentication}


@router.get("/preview")
async def preview_pdf(filename: str, Authentication: str):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    converted_filename = filename.rsplit(".", 1)[0] + ".pdf"
    return FileResponse(f"save_files/{directory}/converted/{converted_filename}")


@router.get("/user/test")
async def user_test():
    print(    global_test.getter('1'))
    return global_test.getter('1')
