import os
from datetime import datetime

from Crypto.Random import random
from dinero import Dinero
from dinero.currencies import CNY
from fastapi import APIRouter, Body, Form, Header
from pydantic import BaseModel
from typing_extensions import Any, Annotated
import json
from pypdf import PdfReader
import logging
import traceback
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeCreateModel import AlipayTradeCreateModel
from alipay.aop.api.response.AlipayTradeCreateResponse import AlipayTradeCreateResponse
from alipay.aop.api.request.AlipayTradePrecreateRequest import (
    AlipayTradePrecreateRequest,
)

import global_var
import jwt
import print_queue

router = APIRouter()


class FileList(BaseModel):
    files: object


@router.post("/pay/createBill")
def create_bill(fileList: FileList, Authentication: Annotated[str | None, Header()]):
    payload = jwt.decode_token(Authentication)
    directory = payload.get("token")
    expire = payload.get("exp")
    files = json.loads(fileList.files)
    filenameArray = []
    price = 0

    for file in files:
        filedict = files.get(file)
        converted_filename = file.rsplit(".", 1)[0] + ".pdf"
        reader = PdfReader(f"save_files/{directory}/converted/{converted_filename}")
        page_number = len(reader.pages)
        if not filedict.get("print_side"):
            price = Dinero(0.2, CNY).multiply(page_number)
        if filedict.get("print_side"):
            if page_number % 2 == 0:
                price = Dinero(0.18, CNY).multiply(page_number)
            else:
                price = Dinero(0.18, CNY).multiply(page_number - 1).add(0.2)

    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filemode="a",
    )
    logger = logging.getLogger("")

    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = "https://openapi.alipay.com/gateway.do"
    alipay_client_config.app_id = "2021004132637514"
    alipay_client_config.app_private_key = "MIIEpAIBAAKCAQEAoJUsean2rCX36yo6EtSSwrmVwyBzi//9t/zdiFtL96OpdXJpEqwzt7MozrFd0dFYxjmmZaLQ/4UejgxR2zghspYD/5dZ+7thE7SoKWqzDQQQPgFelFzDicY6VM25qa+m/5XDmYZz6GvZyWA0PYRms1clXRou5BbUVkomqWlmomsT9y5oLnGsrmhfzcA0z3FuQ86M3IZzgQbAiNHNMOBECOMzUM7GFucwPEwZF8tbNKa1VEclC1BbkCHJdawyYjL8hhuXDSBxOoZ/unDRMy/A/O/NosmtcAHNmPEq2i95CKDuFzDBsupfmkz8sviTSay/hhuISKBN2FzJTyXRw/HGnwIDAQABAoIBAFD0QzKmk5ufnIdqh1Jc5gvS4YQ4ROgMSs1JZilK1VZnpJN39S6br4rpgCYLVp/jKRztjUxps3FNm+TCozWf66ULacKde5ijk0IK7kfK6a8jIEkSCatDxLQdQeTkvbekvMzWpIAuPxqp3GZf4JYuvFOnGEgCXidQtwU1Zp47a6lu/8oB0sjBTcROIS+N3w2VsKeM8ULABqMqR5PE+wQ0JsQy635FlrT6q2R3bSXr4Q2lZIknp2ADts1Mr6qQJJHyhoyqd5T7kAFz91eaX/S+j1jddgXOad0SBklDB7XRnBGwh9oX9ryRhm0Ux8uSxxMmnWHMg+jjFQAguzDKjHK3HqECgYEA9Q5vHIT+49VskP9uC1sONISObCgqn/1YPywf0YsEWktxukpTpF0vnoPB3j6EGD26k0E0OZ3Dj0NutcMDvN52TaXjOoGp5jxYrrjz3Po2g7RVt+qYxAvImPdLxCEZGEyfnUJeMcsFRZnfEQSYQ9HGOe1pucQLNwG5WsV+tWxHPW8CgYEAp8ECNGt/xFFbKfACuG7DpSFrGB0pXZMAPNWutv7XL85mM4FI9/j64HmH/lqpR35Ip9LOmwB9hQOY3z81RSABo+MaOdoD8aTREcc25W4N04OvYNyRBo9/znFs3HwQ7n1I6C0l7b4o8GNSIsERltbv7puJ/WaEwaSX7ERqOMbv0dECgYEAyUn56qsz02FTtCab9aftmyXm9uBnYtNu0TUlTbGq+aBO4n57Bd+lZcdET5F6X48U2jAM/eag4+S344U0ZMc21cEVTNGFBSE8lwhFB5ZfgP94CYIhyacENuGq0od9XYBS+5GwXaYtxmYF3KyxhcOh16Mz3OszaxN3dSAUXGF8gvECgYBVwSa9YU65LtWphJX/bi/5VDII669ftGvkrV9ZEME0IRDBt49zpAWrhrTsY7Axae7+S5duSTvhKUuWpBs5MPllrAyWEkr91kFCE1KOykmrHKAkpdxFPEobYIRD2fBV2hnRBnNjK1iGOl+cgJHbSBjzIvPRY/zteJRpJTgfuiKSYQKBgQCIbX9Lc/R/7OQuzEMZGzUWw4viuU9cUbcS1JkZD+J959/EfBDCINGVOdLEAVo//AUuWf5pAEQTn9xPASKqDZCrg3Veqx47sYf+nL5Eo7vr4AX87MwWniTagmblBTKxQx604C8oTQE1S6w9SWQQfEUH0ZpnYkgm07Z2roNV2T7hZg=="
    alipay_client_config.alipay_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiR4YO4wl+fdo9r/mVJoIZkO+6tIR5cl3ynIguJJRIF5zLfWUHz5ACpmEVsBefuIvcyPe4FCVypR1LsXCcmlq1bv1dIAajZKrxnjD2A+ydITB7DhE+fKxbn2EPg5ax2ttQ7NR6ZedBREmwH9cnJVOmFdQ8tIxKinN3coKqP/6cNyT0TIKUr8OM2dw2oJ9wALHq8yYDbTEtYpVww54ogFJBCD5+z8Eo/yeG1Q/AhaTTPr3sQgUiDcW1ERl/grEqAeq7CBElJC1rGc2lwUky+lcusd2bP8+Utn6fQeyAbymGn1K2LGzXVTBq7G0IVwLq8PqAkP6T+/QdKjjO2m7Hz7lxQIDAQAB"
    client = DefaultAlipayClient(alipay_client_config, logger)

    seed = ""
    for i in range(6):
        seed = seed + str(random.randint(0, 9))

    model = AlipayTradeCreateModel()
    model.out_trade_no = directory + f"_{seed}"
    model.total_amount = 0.01 #price.format()
    model.subject = "30栋304打印店"

    request = AlipayTradePrecreateRequest(biz_model=model)
    request.notify_url = "http://47.106.100.54:8000/pay/return"
    response_content = False
    try:
        response_content = client.execute(request)
    except Exception as e:
        print(traceback.format_exc())

    if not response_content:
        print("failed execute")
    else:
        # 解析响应结果
        response = AlipayTradeCreateResponse()
        string = response.parse_response_content(response_content)
        print("https://qr.alipay.com/" + eval(response.body)['qr_code'].split("/")[-1])
        os.mkdir(f"save_files/print_queue/{directory}_{seed}/")
        for file in files:
            filename = file.rsplit(".", 1)[0] + ".pdf"
            os.replace(f"save_files/{directory}/converted/{filename}",
                       f"save_files/print_queue/{directory}_{seed}/{filename}")
        global_var.global_var_setter(f"{directory}_{seed}_expire", datetime.now().timestamp() + 60 * 60 * 2)
        global_var.global_var_setter(f"{directory}_{seed}_is_paid", False)
        print(seed)
        # 响应成功的业务处理
        if response.is_success():
            # 如果业务成功，可以通过response属性获取需要的值
            result_code = response.code
            if not result_code:
                result_code = 0
            if int(result_code) == 10000:
                print("成功")
            else:
                print("失败")
            return {"message": "https://qr.alipay.com/" + eval(response.body)['qr_code'].split("/")[-1]}
        else:
            # 如果业务失败，可以从错误码中可以得知错误情况，具体错误码信息可以查看接口文档
            print(
                f"{response.code}, {response.msg}, {response.sub_code}, {response.sub_msg}"
            )
        return {"message": "error"}


@router.post("/pay/return")
def pay_return(trade_status: Annotated[str, Form()], out_trade_no: Annotated[str, Form()]):
    if not trade_status == "TRADE_SUCCESS":
        return {"message": "fail"}
    global_var.global_var_setter(f"{out_trade_no}_is_paid", True)
    print_queue.queue_push(out_trade_no)
    return {"message": "success"}

