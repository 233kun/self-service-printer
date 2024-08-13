import asyncio
import os.path
import time
from asyncio import sleep
from os import mkdir
from shutil import copyfile
from typing import Annotated
from threading import Thread
from fastapi import APIRouter, UploadFile, Header, BackgroundTasks
from pydantic import BaseModel
from pypdf import PdfReader
from starlette.responses import FileResponse

import files_attributes_global_var
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
async def create_upload_file(Authentication: Annotated[str | None, Header()], files: list[UploadFile],
                             background_tasks: BackgroundTasks):
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
        print(files)
        with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
            f.write(files[index].file.read())

        file_attributes = FileModel()
        file_attributes.filename = files[index].filename
        file_attributes.convert_state = "processing" # pending
        file_attributes.print_copies = 1
        file_attributes.print_range_start = 1
        file_attributes.print_range_end = 1
        file_attributes.print_side = "one-sided"

        try:
            files_attributes = files_attributes_global_var.getter(directory)
            files_attributes.append(file_attributes)
            files_attributes_global_var.setter(directory, files_attributes)
        except Exception as e:
            files_attributes = [file_attributes]
            files_attributes_global_var.setter(directory, files_attributes)
        # files_attributes = []
        # try:
        #     files_attributes = files_attributes_global_var.getter(directory)
        #     files_attributes.append(file_attributes)
        #     files_attributes_global_var.setter(directory, files_attributes)
        # except BaseException as e:  # when file attributes is empty
        #     files_attributes.append(file_attributes)
        #     files_attributes_global_var.setter(directory, files_attributes)
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
            background_tasks.add_task(convert_docs, directory, files[index].filename)
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

    return ReturnResult(200, "success", files)


@router.get("/uploadfile/filelist")
async def get_folder(Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        expire = payload.get("exp")
        files_attributes = {}
        try:
            return ReturnResult(200, "success", {'files_attributes': files_attributes_global_var.getter(directory)})
            # return ReturnResult(200, "success", {'files_attributes': global_var_getter(directory)})
        except BaseException as e:
            return ReturnResult(200, "success", {'files_attributes': []})


@router.get("/stest")
async def get_ftest(key, value):
    return files_attributes_global_var.setter(key, value)


@router.get("/gtest")
async def get_ftest(key):
    return files_attributes_global_var.getter(key)

    # try:
    #     files_attributes = global_var_getter(directory)
    # except BaseException:
    #     return ReturnResult(200, "success", {'files_attributes': []})
    # else:
    #     print(ReturnResult(200, "success", {'files_attributes': files_attributes_global_var.getter(directory)}))
    #     # return ReturnResult(200, "success", {'files_attributes': files_attributes_global_var.getter(directory)})
    #     print(global_var_getter(directory))
    #     print(files_attributes_global_var.getter(directory))
    #     return ReturnResult(200, "success", {'files_attributes': global_var_getter(directory)})


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
            await sleep(0.001)
            if time.time() - start_unix_timestamp > 120:
                return ReturnResult(200, "timeout", {})
            files_attributes = files_attributes_global_var.getter(directory)
            for file_attributes in files_attributes:
                for converting_filename in converting_filenames:
                    if file_attributes.filename == converting_filename:
                        if file_attributes.convert_state == "success":
                            return ReturnResult(200, "success", {})
    return ReturnResult(200, "success", {})


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
    print(global_test.getter('1'))
    return global_test.getter('1')
