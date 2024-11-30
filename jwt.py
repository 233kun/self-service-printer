import random
from ctypes import Union
from datetime import datetime, timezone, timedelta

from jose import JWTError, jwt, ExpiredSignatureError
import uuid

from setting import SECRET_KEY, ALGORITHM


def create_token():
    expire = datetime.now().timestamp() + 60 * 15
    payload_uuid = str(uuid.uuid4())
    to_encode = {"token": payload_uuid, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        jwt.decode(token, SECRET_KEY)
        return True
    except Exception as e:
        return False


def renew_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    except ExpiredSignatureError:
        return create_token()
    else:
        if payload.get("exp") > datetime.now().timestamp():
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            to_encode = {"token": payload.get("token"), "exp": expire}
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        else:
            return create_token()


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, options={'verify_exp': False})
