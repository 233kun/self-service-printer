import json
import os

import jose
from fastapi import Depends
from asyncio import sleep
from datetime import datetime
from os import mkdir
from typing import Annotated
from fastapi import APIRouter, UploadFile, Header, BackgroundTasks
from jose.jwt import decode
from starlette.responses import FileResponse

import setting
from global_vars.files_attributes_singleton import files_attributes_singleton
from models import FileModel, ReturnResult, RemoveFilename, ConvertFactory
import jwt

router = APIRouter()



@router.put("/uploadfile")
async def create_upload_file(files: list[UploadFile],
                             background_tasks: BackgroundTasks,
                             payload: dict = Depends(jwt.verify_token)):
    directory = payload.get("token")
    if not os.path.exists("uploads/" + directory):
        mkdir(f"uploads/{directory}")
        mkdir(f"uploads/{directory}/raw")
        mkdir(f"uploads/{directory}/converted")

    with open(f'uploads/{directory}/expire', 'w') as f:
        expire = {'expire': datetime.now().timestamp() + 60 * 15}
        json.dump(expire, f)

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
        file_attributes.folder = directory

        files_attributes_global = files_attributes_singleton()
        files_attributes = []
        if directory in files_attributes_global.data:
            files_attributes = files_attributes_global.data.get(directory)
            for file_attribute in files_attributes:
                if file_attribute.filename == files[index].filename:
                    files_attributes.remove(file_attribute)
        files_attributes.append(file_attributes)
        files_attributes_global.data.update({directory: files_attributes})

        filetype = files[index].filename.rsplit(".", 1)[1]

        convert = ConvertFactory().convert(setting.CONVERT_TOOL)
        if filetype == "pdf":
            background_tasks.add_task(convert.convert_pdf, directory, files[index].filename)
        if filetype == "doc" or filetype == "docx":
            background_tasks.add_task(convert.convert_docs, directory, files[index].filename)
        if filetype == "xlsx" or filetype == "xls":
            background_tasks.add_task(convert.convert_excel, directory, files[index].filename)
        if filetype == "jpeg" or filetype == "jpg" or filetype == "png":
            background_tasks.add_task(convert.convert_images, directory, files[index].filename)
    return ReturnResult(200, "success", files)


@router.get("/uploadfile/filelist")
async def get_folder(Authorization: Annotated[str | None, Header()]):
    token = Authorization.split(' ')[1]
    try:
        print(token)
        jose.jwt.decode(token, setting.SECRET_KEY)
    except Exception as e:
        print(e)
        return ReturnResult(200, "success", {'files_attributes': [], 'token': jwt.create_token()})
    renewed_token = jwt.renew_token(token)
    payload = jwt.decode_token(token)
    directory = payload.get("token")

    files_attributes_global = files_attributes_singleton()
    files_attributes = files_attributes_global.data
    if directory in files_attributes:
        with open(f'uploads/{directory}/expire', 'w') as f:
            expire = {'expire': datetime.now().timestamp() + 60 * 15}
            json.dump(expire, f)
        return ReturnResult(200, "success",{'files_attributes': files_attributes.get(directory), 'token': renewed_token})
    return ReturnResult(200, "success", {'files_attributes': [], 'token': renewed_token})

@router.get("/uploadfile/convert_status")
async def get_convert_status(payload: dict = Depends(jwt.verify_token)):
    directory = payload.get("token")
    files_attributes_global = files_attributes_singleton()
    files_attributes = files_attributes_global.data.get(directory)

    converting_filenames = []
    for file_attributes in files_attributes:
        if file_attributes.convert_state == "processing":
            converting_filenames.append(file_attributes.filename)
    if len(converting_filenames) == 0:
        return ReturnResult(200, "success", {})  # if no processing files, return success

    start_unix_timestamp = datetime.now().timestamp()
    while True:
        await sleep(0.01)
        if datetime.now().timestamp() - start_unix_timestamp > 120:
            return ReturnResult(200, "timeout", {})
        files_attributes = files_attributes_global.data.get(directory)
        for file_attributes in files_attributes:
            for converting_filename in converting_filenames:
                if file_attributes.filename == converting_filename:
                    if file_attributes.convert_state == "success":
                        return ReturnResult(200, "success", {})
                    if file_attributes.convert_state == 'error':
                        return ReturnResult(200, "success", {})


@router.post("/uploadfile/remove")
async def remove_file(remove_filename: RemoveFilename, payload: dict = Depends(jwt.verify_token)):
    directory = payload.get("token")
    converted_filename = remove_filename.filename.rsplit(".", 1)[0] + ".pdf"

    files_attributes_global = files_attributes_singleton()
    files_attributes = files_attributes_global.data.get(directory)
    for file_attributes in files_attributes:
        if file_attributes.filename == remove_filename.filename:
            files_attributes.remove(file_attributes)
            break
    files_attributes_global.data.update({directory: files_attributes})
    return ReturnResult(200, "success", {})


@router.get("/preview/{authentication}/{filename}")
async def preview_pdf(authentication, filename):
    if not jwt.verify_token(authentication):
        return {"message": "fail"}
    payload = jwt.decode_token(authentication)
    directory = payload.get("token")
    converted_filename = filename.rsplit(".", 1)[0] + ".pdf"
    return FileResponse(f"uploads/{directory}/converted/{converted_filename}")