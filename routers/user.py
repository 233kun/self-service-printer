import os.path
from datetime import time
from os import mkdir
from shutil import copyfile
from typing import Annotated

from fastapi import APIRouter, UploadFile, Header
from pydantic import BaseModel
from pypdf import PdfReader
from starlette.responses import FileResponse

from global_var import global_var_setter, global_var_getter
from convert import convert_docs, convert_images, convert_excel
from models import FileModel, ReturnResult
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

    files_temp = {}
    for index in range(len(files)):
        file_attribute = FileModel()
        file_attribute.filename = files[index].filename
        file_attribute.convert_state = "processing"
        # file_attribute.total_pages =
        file_attribute.print_copies = 1
        # file_attribute.print_range_start =
        # file_attribute.print_range_end =
        file_attribute.print_side = "one-sided"

        filetype = files[index].filename.rsplit(".", 1)[1]
        if filetype == "pdf":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                copyfile(f'save_files/{directory}/raw/{files[index].filename}',
                         f'save_files/{directory}/converted/{files[index].filename}')
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attribute.convert_state = "error"
                return {"message": "error"}
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attribute.convert_state = "success"

        if filetype == "doc" or filetype == "docx":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                convert_docs(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attribute.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                reader = PdfReader(f"save_files/{directory}/converted/{files[index].filename.rsplit(".", 1)[0]}.pdf")
                file_attribute.print_range_end = len(reader.pages)
                file_attribute.total_pages = len(reader.pages)
                file_attribute.convert_state = "success"

        if filetype == "xlsx" or filetype == "xls":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                convert_excel(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attribute.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attribute.convert_state = "success"

        if filetype == "jpeg" or filetype == "jpg" or filetype == "png":
            with open(f'save_files/{directory}/raw/{files[index].filename}', "wb") as f:
                f.write(files[index].file.read())
            try:
                convert_images(directory, files[index].filename)
            except Exception as e:
                print(e)
                global_var_setter(directory + files[index].filename, "error")
                file_attribute.convert_state = "error"
            else:
                global_var_setter(directory + files[index].filename, "success")
                file_attribute.convert_state = "success"

        files_temp[files[index].filename] = file_attribute
        files_temp2 = {}
    try:
        global_var_getter(directory)
    except BaseException as e:
        global_var_setter(directory, files_temp)
        print(global_var_getter(directory))
    else:
        files_temp2 = global_var_getter(directory)
        files_temp.update(files_temp2)
    return {"message": "success"}


@router.get("/uploadfile/filelist")
async def get_folder(Authentication: Annotated[str | None, Header()]):
    if jwt.verify_token(Authentication):
        payload = jwt.decode_token(Authentication)
        directory = payload.get("token")
        expire = payload.get("exp")
        files_attribute = {}
        try:
            files_attribute = global_var_getter(directory)
            print(files_attribute)
        except BaseException:
            return ReturnResult(200, "success", files_attribute)
        else:
            return ReturnResult(200, "success", files_attribute)
    # return {"message": returnFiles  }


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
