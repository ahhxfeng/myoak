#coding=utf-8

"""
golbal logger generater using giving config
"""

import logging

def get_logger(name, log_file, level=logging.DEBUG):
    logger = logging.getLogger(name)

    formatter = logging.Formatter("[%(levelname)s] [%(asctime)s] [%(filename)s]: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)

    ch_file = logging.FileHandler(log_file, "a")
    ch_file.setLevel(logging.INFO)
    ch_file.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(ch_file)

    

    return logger