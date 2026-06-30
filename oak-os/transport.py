#coding=utf-8
"""
oak-os.tansport 的 Docstring
tansport gather info to the server 
"""

import logging
import requests
import requests.adapters

import logger
import config

class Transport():
    """
    Transport 的 Docstring

    """
    def __init__(self, account, rig_name, tag_name, device_id, timeout=60, retries=3) -> None:
        self.account = account
        self.rig_name = rig_name
        self.tag_name = tag_name
        self.device_id = device_id
        self.timeout = timeout
        self.retries = retries

        self.session = requests.Session()

        adapter = requests.adapters.HTTPAdapter(max_retries=retries)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.info_logger = logging.getLogger("client_info")

        #self.info_logger = logger.get_logger("client_info", config.CollectorConfiguration["LOG_DIR"] + "python_main.log", level=logging.INFO)
        
    def post(self, url, **data):
        data.update(dict(
            account = self.account,
            rig_name = self.rig_name,
            tag_name = self.tag_name,
            device_id = self.device_id
        ))

        self.info_logger.info("post to {}\n data: {}".format(url, data))
        resp = self.session.post(url, json=data, timeout=self.timeout)
        return resp.status_code, resp.text

    def post_with_sign(self, url, retires=None, **data):
        """
        post 校验签名
        """
        data.update(dict(
            account = self.account,
            rig_name = self.rig_name,
            tag_name = self.tag_name,
            device_id = self.device_id
        ))

        if retires == None:
            retires = self.retries
        
        self.info_logger.info("post to {} \n data: {}".format(url, data))
        # TODO
        return None

    def put(self, url, data):

        params = dict(
            account = self.account,
            rig_name = self.rig_name,
            tag_name = self.tag_name,
            device_id = self.device_id,
        )
        
        