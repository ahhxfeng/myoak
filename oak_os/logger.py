#coding=utf-8

# TODO
# done in home
import logging


def setup_logger(name:str, file:str, level=logging.INFO):
    logger = logging.getLogger()
    return logger 