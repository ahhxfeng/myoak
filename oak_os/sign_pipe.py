# coding=utf-8
# !注意不要保留私钥

import os
import requests
import time


def init(pubkey_path=None):
    # public key 不存在 在脚本目录下找public key
    if pubkey_path is None:
        pubkey_path = os.path.dirname(os.path.realpath("__name__"))
        pubkey_path = os.path.join(pubkey_path, "key_selected.pem")
    set_public_key(pubkey_path)


# 收数据只需要public key
g_pubkey = None


def set_public_key(pubkey_path):
    global g_pubkey
    with open(pubkey_path, "rb") as f:
        g_pubkey = f.read()
    assert RSA.load_pub_key(pubkey_path).check_key(), 'key verification failed'


def verify(data, signature):
    """
    @parms data 应该是binary
    """
    # TODO


def post(url, body=None, timeout=90, retry_limit=3, retry_interval=2.5):
    for retry in range(retry_limit):
        try:
            code, content = _post_once(url, body, timeout)
            if int(code/100) == 2:
                return code, content
        except Exception as e:
            if retry >= retry_limit - 1:
                raise e
        time.sleep(retry_interval)
    raise Exception("retry exceed tolerance")


def _post_once(url, body=None, timeout=90):
    """
    http POST 请求 校验签名

    @return requests.Response
    """

    response = requests.post(
        url=url, json=body, timeout=timeout, allow_redirects=True)
    code = response.status_code
    content = response.content
    if code == 204:
        return code, content
    elif int(code/100) != 2:
        return code, content

    # 2** 时签名
    if "OakSign" not in response.headers:
        raise Exception("miss sign")
    signature = response.headers["OakSign"]
    if not verify(signature, content):
        raise Exception("invalid sign")
    return code, content
