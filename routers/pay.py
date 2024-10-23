import os
import time
from datetime import datetime

from Crypto.Random import random
from dinero import Dinero
from dinero.currencies import CNY
from fastapi import APIRouter, Form, Header
from starlette.responses import HTMLResponse
from typing_extensions import Annotated

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
import setting
from global_vars import bills_global_var
from global_var import global_var_isKey_exist
from models import FileList
from print_queue import queue_push

router = APIRouter()


@router.post("/pay/bill/create")
def create_bill(request_body: FileList, Authentication: Annotated[str | None, Header()]):
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")
    files_attributes = request_body.fileList
    price = Dinero(0, CNY)
    for file_attributes in files_attributes:
        print_side = file_attributes.get('print_side')
        print_copies = file_attributes.get('print_copies')
        print_range_start = file_attributes.get('print_range_start')
        print_range_end = file_attributes.get('print_range_end')
        print_page_number = print_range_end - print_range_start + 1

        if print_side == 'one-sided':
            price = Dinero(0.2, CNY).multiply(print_page_number).multiply(int(print_copies)).add(price)
        if print_side == "two-sided-default" or print_side == "two-sided-short-edge" or print_side == "two-sided-long-edge":
            if print_page_number % 2 == 0:
                price = Dinero(0.15, CNY).multiply(print_page_number).multiply(int(print_copies)).add(price)
            else:
                price = Dinero(0.15, CNY).multiply(print_page_number - 1).add(0.2).multiply(int(print_copies)).add(price)
    out_trade_no = datetime.now().strftime('%Y%m%d%H%M%S%f')
    bill_attributes = {'files_attributes': files_attributes, 'folder': directory, 'total_price': float(price.format()), 'out_trade_no': out_trade_no, 'expiry': int(time.time()) + 60 * 60 * 3 + 60}
    bills_global_var.setter(out_trade_no, bill_attributes)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="a",
    )
    logger = logging.getLogger("")

    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = "https://openapi.alipay.com/gateway.do"
    # 别看了，已失效
    alipay_client_config.app_id = setting.app_id
    alipay_client_config.app_private_key = setting.alipay_private_key
    alipay_client_config.alipay_public_key = setting.alipay_public_key
    client = DefaultAlipayClient(alipay_client_config, logger)

    model = AlipayTradeCreateModel()
    model.out_trade_no = bill_attributes.get('out_trade_no')
    model.total_amount = bill_attributes.get('total_price')
    model.subject = "30栋304打印店"

    request = AlipayTradePrecreateRequest(biz_model=model)
    request.notify_url = "https://47.106.100.54:8000/pay/return"
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
                print("失败")
            return {"message": "https://qr.alipay.com/" + eval(response.body)['qr_code'].split("/")[-1]}
        else:
            print(
                f"{response.code}, {response.msg}, {response.sub_code}, {response.sub_msg}"
            )
        return {"message": "error"}


@router.post("/pay/return")
def pay_return(trade_status: Annotated[str, Form()], out_trade_no: Annotated[str, Form()]):
    if not trade_status == 'TRADE_SUCCESS':
        return {"message": "error"}
    # if global_var_isKey_exist:
    #     return HTMLResponse(content="success", status_code=200)
    bill_attributes = bills_global_var.getter(out_trade_no)
    files_attributes = bill_attributes.get('files_attributes')
    for file_attributes in files_attributes:
        folder = bill_attributes.get('folder')
        converted_filename = file_attributes.get('filename').rsplit(".", 1)[0] + '.pdf'
        os.mkdir(f'print_queue/{folder}')
        os.replace(f'save_files/{folder}/converted/{converted_filename}', f"print_queue/{folder}/{converted_filename}")
    queue_push(bill_attributes)
    return HTMLResponse(content="success", status_code=200)