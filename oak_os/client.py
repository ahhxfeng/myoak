# coding=utf-8
import re
import uuid
import hashlib

import tools
import sysinfo


class NoneAccountError(Exception):
    pass


class CollectorClient(object):
    def __init__(self, config) -> None:
        self.config = config

        self.account, self.rig_name = self._get_account(
            self.config["ACCOUNT_CONFIG_PATH"])
        self.tag_name = self._get_tag(self.config["TAG_CONFIG_PATH"])
        # self.transport = transport.Transport()
        self.version = self._get_version()
        self.is_registered = False
        self.device_id = self._get_device_id()

    def _get_account(self, path):
        account, rig_name = tools.read_account(path)
        if account is None:
            raise NoneAccountError
        return account, rig_name

    def _get_tag(self, path):
        tag_name = tools.read_tag(path)
        if tag_name is None:
            tag_name = "default"
        return tag_name

    def _get_version(self):
        return None

    def _get_mac_address(self):
        node = uuid.getnode()
        mac = uuid.UUID(int=node).hex[-12:]
        mac = '-'.join(re.findall(r'.{2}', mac)).upper()
        return mac

    def _get_device_id(self):
        return hashlib.sha1(self._get_mac_address()).hexdigest()

    def version_handler(self):
        """
        version handler 
        """
        # TODO
        # return None

    def report_handler(self):
        data = sysinfo.get_video_card_info()
        
