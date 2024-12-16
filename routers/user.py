import os.path
import time
from asyncio import sleep
from datetime import datetime, timezone, timedelta
from os import mkdir
from shutil import copyfile
from typing import Annotated
from fastapi import APIRouter, UploadFile, Header, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import FileResponse

from global_vars import files_attributes_global_var, expire_global_var
from global_var import global_var_setter
from convert import convert_docs, convert_images, convert_excel, convert_pdf
from models import FileModel, ReturnResult, RemoveFilename, JwtToken
import jwt

router = APIRouter()

# ** DEPRECATED **

# @router.get("/token/generation")
# async def get_token():
#     token = jwt.create_token()
#     expire_global_var.renew_expire(token)
#     return ReturnResult(200, "success", {"token": token})
#
#
# @router.post("/token/renew")
# async def renew_token(jwt_token: JwtToken):
#     expire_global_var.renew_expire(jwt_token.token)
#     return ReturnResult(200, "success", {"token": jwt.renew_token(jwt_token.token.__str__())})


@router.put("/uploadfile")
async def create_upload_file(Authentication: Annotated[str | None, Header()], files: list[UploadFile],
                             background_tasks: BackgroundTasks):
    if not jwt.verify_token(Authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")

    if not os.path.exists("uploads/" + directory):
        mkdir(f"uploads/{directory}")
        mkdir(f"uploads/{directory}/raw")
        mkdir(f"uploads/{directory}/converted")

    for index in range(len(files)):
        with open(f'uploads/{directory}/raw/{files[index].filename}', "wb") as f:
            f.write(files[index].file.read())

        file_attributes = FileModel()
        file_attributes.filename = files[index].filename
        file_attributes.convert_state = "processing"  # pending
        file_attributes.print_copies = 1
        file_attributes.print_range_start = 1
        file_attributes.print_range_end = 1
        file_attributes.print_side = "one-sided"

        try:
            files_attributes_global = files_attributes_global_var.getter(directory)
            for file_attributes_global in files_attributes_global:
                if file_attributes_global.filename == files[index].filename:
                    file_attributes_global.remove(file_attributes_global)
            files_attributes_global.append(file_attributes)
            files_attributes_global_var.setter(directory,  files_attributes_global)

        except Exception as e:
            files_attributes = [file_attributes]
            files_attributes_global_var.setter(directory,  files_attributes)
            expire_global_var.setter(directory, datetime.now().timestamp() + 60 * 15)

        filetype = files[index].filename.rsplit(".", 1)[1]
        if filetype == "pdf":
            background_tasks.add_task(convert_pdf, directory, files[index].filename)
        if filetype == "doc" or filetype == "docx":
            background_tasks.add_task(convert_docs, directory, files[index].filename)
        if filetype == "xlsx" or filetype == "xls":
            background_tasks.add_task(convert_excel, directory, files[index].filename)
        if filetype == "jpeg" or filetype == "jpg" or filetype == "png":
            background_tasks.add_task(convert_images, directory, files[index].filename)
    return ReturnResult(200, "success", files)


@router.get("/uploadfile/filelist")
async def get_folder(Authentication: Annotated[str | None, Header()]):
    if Authentication == 'none':
        token = jwt.create_token()
        return ReturnResult(200, "success", {'files_attributes': [], 'token': token})
    if not jwt.verify_token(Authentication):
        token = jwt.create_token()
        return ReturnResult(200, "success", {'files_attributes': [], 'token': token})
    else:
        renewed_token = jwt.renew_token(Authentication)
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        expire = payload.get("exp")

        try:
             expire_global_var.setter(directory, datetime.now().timestamp() + 60 * 15)
             return ReturnResult(200, "success", {'files_attributes': files_attributes_global_var.getter(directory), 'token': renewed_token})
        except KeyError as e:
            return ReturnResult(200, "success", {'files_attributes': [], 'token': renewed_token})
        except Exception as e:
            return ReturnResult(200, "初始化失败", {})


@router.get("/uploadfile/convert_status")
async def get_convert_status(Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")

        files_attributes = files_attributes_global_var.getter(directory)

        converting_filenames = []
        for file_attributes in files_attributes:
            if file_attributes.convert_state == "processing":
                converting_filenames.append(file_attributes.filename)
        if len(converting_filenames) == 0:
            return ReturnResult(200, "success", {})  # if no processing files, return success

        start_unix_timestamp = time.time()
        while True:
            await sleep(0.01)
            if time.time() - start_unix_timestamp > 120:
                return ReturnResult(200, "timeout", {})
            files_attributes = files_attributes_global_var.getter(directory)
            for file_attributes in files_attributes:
                for converting_filename in converting_filenames:
                    if file_attributes.filename == converting_filename:
                        if file_attributes.convert_state == "success":
                            return ReturnResult(200, "success", {})
    return ReturnResult(200, "success", {})


@router.post("/uploadfile/remove")
async def remove_file(remove_filename: RemoveFilename, Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        converted_filename = remove_filename.filename.rsplit(".", 1)[0] + ".pdf"

        files_attributes = files_attributes_global_var.getter(directory)
        for file_attributes in files_attributes:
            if file_attributes.filename == remove_filename.filename:
                files_attributes.remove(file_attributes)
        files_attributes_global_var.setter(directory, files_attributes)
        return ReturnResult(200, "success", {})


@router.get("/preview/{authentication}/{filename}")
async def preview_pdf(authentication, filename):
    if not jwt.verify_token(authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(authentication)
    directory = payload.get("token")
    converted_filename = filename.rsplit(".", 1)[0] + ".pdf"
    return FileResponse(f"uploads/{directory}/converted/{converted_filename}")