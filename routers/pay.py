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
    alipay_client_config.app_id = "2021004132637514"
    # alipay_client_config.app_private_key = "MIIEpAIBAAKCAQEAoJUsean2rCX36yo6EtSSwrmVwyBzi//9t/zdiFtL96OpdXJpEqwzt7MozrFd0dFYxjmmZaLQ/4UejgxR2zghspYD/5dZ+7thE7SoKWqzDQQQPgFelFzDicY6VM25qa+m/5XDmYZz6GvZyWA0PYRms1clXRou5BbUVkomqWlmomsT9y5oLnGsrmhfzcA0z3FuQ86M3IZzgQbAiNHNMOBECOMzUM7GFucwPEwZF8tbNKa1VEclC1BbkCHJdawyYjL8hhuXDSBxOoZ/unDRMy/A/O/NosmtcAHNmPEq2i95CKDuFzDBsupfmkz8sviTSay/hhuISKBN2FzJTyXRw/HGnwIDAQABAoIBAFD0QzKmk5ufnIdqh1Jc5gvS4YQ4ROgMSs1JZilK1VZnpJN39S6br4rpgCYLVp/jKRztjUxps3FNm+TCozWf66ULacKde5ijk0IK7kfK6a8jIEkSCatDxLQdQeTkvbekvMzWpIAuPxqp3GZf4JYuvFOnGEgCXidQtwU1Zp47a6lu/8oB0sjBTcROIS+N3w2VsKeM8ULABqMqR5PE+wQ0JsQy635FlrT6q2R3bSXr4Q2lZIknp2ADts1Mr6qQJJHyhoyqd5T7kAFz91eaX/S+j1jddgXOad0SBklDB7XRnBGwh9oX9ryRhm0Ux8uSxxMmnWHMg+jjFQAguzDKjHK3HqECgYEA9Q5vHIT+49VskP9uC1sONISObCgqn/1YPywf0YsEWktxukpTpF0vnoPB3j6EGD26k0E0OZ3Dj0NutcMDvN52TaXjOoGp5jxYrrjz3Po2g7RVt+qYxAvImPdLxCEZGEyfnUJeMcsFRZnfEQSYQ9HGOe1pucQLNwG5WsV+tWxHPW8CgYEAp8ECNGt/xFFbKfACuG7DpSFrGB0pXZMAPNWutv7XL85mM4FI9/j64HmH/lqpR35Ip9LOmwB9hQOY3z81RSABo+MaOdoD8aTREcc25W4N04OvYNyRBo9/znFs3HwQ7n1I6C0l7b4o8GNSIsERltbv7puJ/WaEwaSX7ERqOMbv0dECgYEAyUn56qsz02FTtCab9aftmyXm9uBnYtNu0TUlTbGq+aBO4n57Bd+lZcdET5F6X48U2jAM/eag4+S344U0ZMc21cEVTNGFBSE8lwhFB5ZfgP94CYIhyacENuGq0od9XYBS+5GwXaYtxmYF3KyxhcOh16Mz3OszaxN3dSAUXGF8gvECgYBVwSa9YU65LtWphJX/bi/5VDII669ftGvkrV9ZEME0IRDBt49zpAWrhrTsY7Axae7+S5duSTvhKUuWpBs5MPllrAyWEkr91kFCE1KOykmrHKAkpdxFPEobYIRD2fBV2hnRBnNjK1iGOl+cgJHbSBjzIvPRY/zteJRpJTgfuiKSYQKBgQCIbX9Lc/R/7OQuzEMZGzUWw4viuU9cUbcS1JkZD+J959/EfBDCINGVOdLEAVo//AUuWf5pAEQTn9xPASKqDZCrg3Veqx47sYf+nL5Eo7vr4AX87MwWniTagmblBTKxQx604C8oTQE1S6w9SWQQfEUH0ZpnYkgm07Z2roNV2T7hZg=="
    # alipay_client_config.alipay_public_key = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiR4YO4wl+fdo9r/mVJoIZkO+6tIR5cl3ynIguJJRIF5zLfWUHz5ACpmEVsBefuIvcyPe4FCVypR1LsXCcmlq1bv1dIAajZKrxnjD2A+ydITB7DhE+fKxbn2EPg5ax2ttQ7NR6ZedBREmwH9cnJVOmFdQ8tIxKinN3coKqP/6cNyT0TIKUr8OM2dw2oJ9wALHq8yYDbTEtYpVww54ogFJBCD5+z8Eo/yeG1Q/AhaTTPr3sQgUiDcW1ERl/grEqAeq7CBElJC1rGc2lwUky+lcusd2bP8+Utn6fQeyAbymGn1K2LGzXVTBq7G0IVwLq8PqAkP6T+/QdKjjO2m7Hz7lxQIDAQAB"
    alipay_client_config.app_private_key = 'MIIEowIBAAKCAQEAr75MJKJdLtyxcr95SPLXZ9wnILgxjMuIq2AqwPxuiUgl6igsPO745d04OVRA2CW/aQA6TLvv0551eq1OALIe9uFj1/InWBN3E9tTQhFGGDxmDn/5yHxkn5JGBFCDQGphTJcHzM/tx7fPTwrVdXOxqVxHzGJWeX5rdr5kf07dcwE/EqrWKAj+FRwHGXSgqiX+zzc5w+razTsQsoPLOevsHvrEIdkQXZjQR9EHffd5lrw0bYnvDuxX99rUsm/dorQ/Yi6bGBpD2MdIe4JmebPAls19mb9GBAO7HjRHqFxKsx1MK/X5+cybl4RIm3yDV/ov28+wOHaCkaI2+TGZrIzMxwIDAQABAoIBAA8duiTohkVSnDy3dXIt2RNI32C0Fyb6Fr5O3j6NN+C9AO3cGLoBAA2dcomT0qQE0yrv5xPUknNMTOSJZY0vxPQNPO5FGNc9jV963PVw0OuivlB+93gkIu+KwFT8q91tiQLydqxKMjScfctZrjSVB/H+Svqsdq2qjwm+pJxCp0+N5j4W35E/a6vUK3y3YijNq5SGxbHMvo3lnFjNxATWD8tRFWZtsjG/3kaGlFbgXScVtUNxK7hhysLgakLcTCgz/fV84p2suzDq8+Bk93BqinPdpA1oF6JFG4wnGWV2O2oN70d5BBqRFhm1hSRDwvGcDbATZXQsRJBWglL7Cj49XQECgYEA6N7yv1mQqRZ6Vt61jiUXuy8tDVmCL8Xva6LOqFo3vKtM5isyocddu9bUblgP1q6n5GVS7INv7g7eeDP7Ktko1JmtqkG2Q23WVJL5+am0+bKpi8ymiOdY0G2LKeH2uwTewod06wRfCy1nIqthNHm/wEiD4ox/Yj39OmrrZ5dq2YECgYEAwTLOOK4XGpSkWn4Z/00RVbyLOw74V7WtunphZoOCYfsQhQTn5Bk/e+CH2CmNK33/f0GNpyV2XfswWrXV+ZC5gVURWnIOCeE9HywdzMz/sPAI4aGsj2ioSoCVPs+h98HNTgpmdwWKmVMyaKlDzt+6IIx661jHdAsGGPZ7upXDekcCgYBc7cN/WtWgtGijzAI1tFWxDBV1c1fBisKNeI3xnvcJIm7wlyKAbtfYAtYJJrlDWbWELm8WFSmQnXxoCY5cvgZOOPmVrN14MRfL7k81M2UWFBcWw9ddYL0Ph/d2Akd8wGfIx1eABeGLy1WR/0QuNbuwlv+SY7Dd2pD4Q/ym/UTVgQKBgCAn8KMGdtn5u5FEQ9d2YFhA1Xuy9irDFnNfQy7o3J6qRwmc02vnt+VKbdHQuKpwgkIQCx+y4Iyr7lRqx36OVBHussC3ExcZ4i56DUu1Iym0CgZj/nCwHrKnzC90J6UxIJbIrF1LEtKKQm2hHqQkILqiJyNc13W9D/q/q8BWhP6pAoGBAK8085Kf4z0er2gkuddn1qkqAuwSNC+GSciHKwooAX866i/0bz9urtGvlCRulksHIvn8BRBdkOMykCln/gDti4vGdaUoErnUOQIBBis3O8ZJMHHI4owIcl2OnOVun28xiNINwOASwa6XWQqwU6Bb6ujwOJvg/A8l0QEDjgT5Jmqm'
    alipay_client_config.alipay_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiR4YO4wl+fdo9r/mVJoIZkO+6tIR5cl3ynIguJJRIF5zLfWUHz5ACpmEVsBefuIvcyPe4FCVypR1LsXCcmlq1bv1dIAajZKrxnjD2A+ydITB7DhE+fKxbn2EPg5ax2ttQ7NR6ZedBREmwH9cnJVOmFdQ8tIxKinN3coKqP/6cNyT0TIKUr8OM2dw2oJ9wALHq8yYDbTEtYpVww54ogFJBCD5+z8Eo/yeG1Q/AhaTTPr3sQgUiDcW1ERl/grEqAeq7CBElJC1rGc2lwUky+lcusd2bP8+Utn6fQeyAbymGn1K2LGzXVTBq7G0IVwLq8PqAkP6T+/QdKjjO2m7Hz7lxQIDAQAB'
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
        # 解析响应结果
        response = AlipayTradeCreateResponse()
        string = response.parse_response_content(response_content)
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
    if not trade_status == 'TRADE_SUCCESS':
        return {"message": "error"}
    # if global_var_isKey_exist:
    #     return HTMLResponse(content="success", status_code=200)
    bill_attributes = bills_global_var.getter(out_trade_no)
    files_attributes = bill_attributes.get('files_attributes')
    for file_attributes in files_attributes:
        folder = bill_attributes.get('folder')
        filename = file_attributes.get('filename')
        os.replace(f'save_files/{folder}/{filename}', f"print_queue/{folder}/{filename}")
    queue_push(bill_attributes)
    return HTMLResponse(content="success", status_code=200)

