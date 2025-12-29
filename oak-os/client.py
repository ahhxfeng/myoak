#coding=utf-8

"""
oak os client
gather the collected data and post to the bkend
author: TF
version: 1.0.0
2025@copyright all right reserved

"""
import hashlib
import logging
import os
import uuid
import re

import wget


import tools
import logger
from config import CollectorConfiguration

class NoAccountError(Exception):
    pass


class InvalidUserError(Exception):
    def __init__(self, account):
        super(InvalidUserError, self).__init__
        self.account = account
class UnknownError(Exception):
    def __init__(self, account):
        super(UnknownError, self).__init__()


class DownloadError(Exception):
    def __init__(self, url, md5sum):
        super(DownloadError, self).__init__()
        self.url = url
        self.md5sum = md5sum


class UnsupportedFileType(Exception):
    def __init__(self, info=None):
        super(UnsupportedFileType, self).__init__()
        self.info = info


class UnsupportedAction(Exception):
    def __init__(self, info=None):
        super(UnsupportedAction, self).__init__()

class VersionMark():
    """
    version mark class help to manage the oak version 
    """
    VERSION_FILE = "version"
    def __init__(self) -> None:
        self.version = None

    def load(self, path):
        try:
            with open(path, "r") as f:
                return f.read().strip()
        except Exception as e:
            return None
        
    def save(self, path):
        with open(path, "w") as f:
            f.write(str(self.version))

    def __enter__(self):
        self.version = self.load(VersionMark.VERSION_FILE)
        return self
    
    def __exit__(self, type):
        if type is None and self.version is not None:
            self.save(VersionMark.VERSION_FILE)

class Collecter():
    # collertor client
    def __init__(self, config):
        self.config = config

        self.info_log = logger.get_logger("oak_info", CollectorConfiguration["ERROR_LOG_DIR"][0] + "python_main.log", level=logging.INFO)
        self.warn_log = logger.get_logger("oak_warn", CollectorConfiguration["ERROR_LOG_DIR"][0] + "python_main_err.log", level=logging.WARN)

    def _read_account(self, path):
        account, rig_name = tools.read_account(path)
        if account is None:
            raise NoAccountError()
        return account, rig_name
    def _read_tag(self, path):
        tag_name = tools.read_tag(path)
        if tag_name is None:
            return "deafult"
        return tag_name

    def _get_mac_address(self):
        node = uuid.getnode()
        mac = uuid.UUID(int=node).hex[-12:]
        mac = '-'.join(re.findall(r'.{2}', mac)).upper()
        return mac
    
    def _get_device_id(self):
         return hashlib.sha1(self._get_mac_address().encode("utf-8")).hexdigest()
    def _md5sum(self, filepath):
        """
        @return None if md5sum not work
        """
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return None
        
    def _download(self, url, expect_md5, max_reties=3):
        """
        download with checksum if not expect delete
        """
        for _ in range(0, max_reties):
            self.info_log.info("Download %s", url)
            downloaded = wget.download(url, out="/tmp", bar=None)
            downloaded_md5 = self._md5sum(downloaded)
            self.info_log.info("  %s download complete, md5:%s ", (downloaded, downloaded_md5))
            if downloaded_md5 is not None and downloaded_md5 == expect_md5:
                return downloaded
            else:
                os.remove(downloaded)
        return None


    def _update(self):
        pass
    def version_handler(self):
        """
        check the current version and compare with version on server 
        if older than do update
        """
        # get the current verson on server
        pass
    def report_handler(self):
        #TODO
        
    def miner_handler(self):
        pass
    def command_handler(self):
        pass
    def scan_dir(self):
        pass
    def scan_and_upload(self):
        pass

    
    



        
        

