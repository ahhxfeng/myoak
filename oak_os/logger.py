#coding=utf-8

<<<<<<< HEAD
import logging

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    gen a logger with given config
    """

    logger = logging.getLogger(name)
    handle_sh = logging.StreamHandler()
    handle_fh = logging.FileHandler(log_file)

    formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(filename)s]: %(message)s')

    handle_sh.setFormatter(formatter)
    handle_fh.setFormatter(formatter)

    logger.addHandler(handle_fh)
    logger.addHandler(handle_sh)
    # set the logger level if not something will miss
    logger.setLevel(level=level)

    return logger

    
=======
# TODO
# done in home
import logging


def setup_logger(name:str, file:str, level=logging.INFO):
    logger = logging.getLogger()
    return logger 
>>>>>>> fb9384fbe42c6cbb3e0656ecc8a01519dfab7551
