#coding=utf-8

"""
oak os tools
all useful tools in this file 
author: TF00
version: 1.0.0
"""

import logger
import logging
def read_account(account_path):
    """
    @return None 如果没有设置账号
    """

    try:
        with open(account_path, "r") as f:
            account = ''
            rig_name = ''
            for line in f.readlines():
                line = line.strip()
                # 略过空行和注释行
                if line == '':
                    continue
                if line[0] == '#':
                    continue
                if account == '':
                    account = line[:21]
                elif rig_name == '':
                    rig_name = line[:21]
            # 空文本情况返回None
            if account == '':
                account = None
            return account, rig_name
    except Exception as e:
        warn_logger = logger.get_logger("oak_warn", level=logging.WARN)
        info_logger = logger.get_logger("oak_info", level=logging.INFO)
        warn_logger.exception(e)
        info_logger.exception(e)
        return None, None
    
def read_tag(tag_path):
    """
    @return default 如果没有设置
    """

    try:
        with open(tag_path, "r") as f:    
            tag_name=""
            for line in f.readlines():
                line = line.strip()
                #略过空行和注释行
                if line == '':
                    continue
                if line[0] == '#':
                    continue
                if tag_name == '':
                    tag_name = line[:21]
            if tag_name == "":
                return "default"
            return tag_name
    except Exception as e:
        warn_logger = logger.get_logger("oak_warn", level=logging.WARN)
        info_logger = logger.get_logger("oak_info", level=logging.INFO)
        warn_logger.exception(e)
        info_logger.exception(e)
        return "default"

        

