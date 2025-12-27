#coding=utf-8

"""
oak log generater
all logger creater from this interface
author: TF
version: 1.0.0

"""

import logging
from logging.handlers import RotatingFileHandler

def get_logger(name, file, level=logging.INFO) ->logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.Handler(level=level)
    file_handler = RotatingFileHandler(file, "a", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
    formater = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(filename)s]: %(message)s')
    #logger.addHandler(handler.setFormatter(formater))
    handler.setFormatter(formater)
    file_handler.setFormatter(formater)

    logger.addHandler(handler)
    logger.addHandler(file_handler)
    return logger