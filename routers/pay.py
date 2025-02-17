import os
import time
from datetime import datetime

from Crypto.Random import random
from alipay.aop.api.util.SignatureUtils import verify_with_rsa
from dinero import Dinero
from dinero.currencies import CNY
from fastapi import APIRouter, Form, Header
from starlette.responses import HTMLResponse
from typing_extensions import Annotated
from jose.jwt import encode
import logging
import traceback
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeCreateModel import AlipayTradeCreateModel
from alipay.aop.api.response.AlipayTradeCreateResponse import AlipayTradeCreateResponse
from alipay.aop.api.request.AlipayTradePrecreateRequest import (
    AlipayTradePrecreateRequest,
)

import jwt
from global_vars.files_attributes_singleton import files_attributes_singleton
from setting import SERVER_HOST, APP_ID, ALIPAY_PRIVATE_KEY, ALIPAY_PUBLIC_KEY, SECRET_KEY
from global_vars import bills_global_var, files_attributes_global_var, expire_global_var
from global_var import global_var_isKey_exist
from models import FileList, ReturnResult
from print_queue import queue_push
from fastapi import FastAPI, Request
from global_vars.bills_attributes_singleton import bills_attributes_singleton

router = APIRouter()


@router.post("/pay/bill/create")
async def create_bill(request_body: FileList, Authentication: Annotated[str | None, Header()]):
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")
    request_body_attributes = request_body.fileList
    files_attributes_global = files_attributes_singleton()
    files_attributes = files_attributes_global.data.get(directory)
    price = Dinero(0, CNY)

    for file_attributes in request_body_attributes:
        print_filename = file_attributes.get("filename")
        print_side = file_attributes.get('print_side')
        try:
            print_copies = int(file_attributes.get('print_copies'))
            print_range_start = int(file_attributes.get('print_range_start'))
            print_range_end = int(file_attributes.get('print_range_end'))
        except Exception as e:
            return ReturnResult(200, '订单不合法', {})

        for file_attributes in files_attributes:
            if print_filename == file_attributes.filename:
                if file_attributes.total_pages < print_range_end:
                    return ReturnResult(200, '订单打印范围不合法', {})

        if print_range_end < print_range_start:
            return ReturnResult(200, '订单打印范围不合法', {})
        if print_copies < 1:
            return ReturnResult(200, '订单打印份数不合法', {})
        if print_side == 'one-sided' or print_side == 'two-sided-default' or print_side == 'two-sided-short-edge' or print_side == 'two-sided-long-edge':
            pass
        else:
            return ReturnResult(200, '订单打印份打印方向不合法', {})

        print_page_number = print_range_end - print_range_start + 1
        if print_side == 'one-sided':
            price = Dinero(0.2, CNY).multiply(print_page_number).multiply(int(print_copies)).add(price)
        if print_side == "two-sided-default" or print_side == "two-sided-short-edge" or print_side == "two-sided-long-edge":
            if print_page_number % 2 == 0:
                price = Dinero(0.15, CNY).multiply(print_page_number).multiply(int(print_copies)).add(price)
            else:
                price = Dinero(0.15, CNY).multiply(print_page_number - 1).add(0.2).multiply(int(print_copies)).add(
                    price)

        # file_attributes.update({'folder': directory}) # pending to rewrite

    out_trade_no = datetime.now().strftime('%Y%m%d%H%M%S%f')
    bill_attributes = {'files_attributes': files_attributes, 'total_price': float(price.format()),
                       'out_trade_no': out_trade_no, 'expiry': time.time() + 60 * 60 * 3}

    if directory in files_attributes_global.data:
        files_attributes_global.data.pop(directory)
    else:
        return ReturnResult(200, '订单生成错误', {})

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="a",
    )
    logger = logging.getLogger("")

    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = "https://openapi.alipay.com/gateway.do"
    # 别看了，已失效
    alipay_client_config.app_id = APP_ID
    alipay_client_config.app_private_key = ALIPAY_PRIVATE_KEY
    alipay_client_config.alipay_public_key = ALIPAY_PUBLIC_KEY
    client = DefaultAlipayClient(alipay_client_config, logger)

    model = AlipayTradeCreateModel()
    model.out_trade_no = bill_attributes.get('out_trade_no')
    model.total_amount = bill_attributes.get('total_price')
    model.subject = "30栋304打印店"
    model.timeout_express = '15m'
    to_encode = {'out_trade_no': bill_attributes.get('out_trade_no')}
    encode_jwt = encode(to_encode, SECRET_KEY, algorithm='HS256')
    model.body = encode_jwt
    print(encode_jwt)
    print(type(encode_jwt))
    print(encode_jwt)

    request = AlipayTradePrecreateRequest(biz_model=model)

    request.notify_url = f"https://{SERVER_HOST}/pay/return"
    response_content = False
    try:
        response_content = client.execute(request)
    except Exception as e:
        print(traceback.format_exc())

    if not response_content:
        print("failed execute")
    else:
        response = AlipayTradeCreateResponse()
        string = response.parse_response_content(response_content)
        if response.is_success():
            result_code = response.code
            if not result_code:
                result_code = 0
            if int(result_code) == 10000:
                print("成功")
            else:
                bills_attributes_global = bills_attributes_singleton()
                bills_attributes_global.data.update({out_trade_no: bill_attributes})
                return "https://qr.alipay.com/" + eval(response.body)['qr_code'].split("/")[-1]
            return ReturnResult(200, 'success',
                                {'url': "https://qr.alipay.com/" + eval(response.body)['qr_code'].split("/")[-1]})
        else:
            print(
                f"{response.code}, {response.msg}, {response.sub_code}, {response.sub_msg}"
            )
        return {"message": "error"}


@router.post("/pay/return")
async def pay_return(trade_status: Annotated[str, Form()], out_trade_no: Annotated[str, Form()],
                     body: Annotated[str, Form()]):
    if not trade_status == 'TRADE_SUCCESS':
        return {"message": "error"}
    if not jwt.verify_token(body):
        return {"message": "error"}
    jwt_payload = jwt.decode_token(body)
    if not jwt_payload.get('out_trade_no') == out_trade_no:
        return {"message": "error"}
    bills_attributes_global = bills_attributes_singleton()
    if out_trade_no in bills_attributes_global.data:
        bill_attributes = bills_attributes_global.data.get(out_trade_no)
        bills_attributes_global.data.pop(out_trade_no)
    else:
        return HTMLResponse(content='success', status_code=200)
    files_attributes = bill_attributes.get('files_attributes')
    for file_attributes in files_attributes:
        folder = file_attributes.get('folder')
        converted_filename = file_attributes.get('filename').rsplit(".", 1)[0] + '.pdf'
        if not os.path.isdir(f'pending_files/{folder}'):
            os.mkdir(f'pending_files/{folder}')
        os.replace(f'uploads/{folder}/converted/{converted_filename}',
                   f"pending_files/{folder}/{converted_filename}")
        # file_attributes.update({'folder': f'{folder}'})
        job_attributes = file_attributes
        queue_push(job_attributes)
    return HTMLResponse(content='success', status_code=200)
