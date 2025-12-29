#coding=utf-8

import logging
import time
import client
import config
from logger import get_logger

def main():
    #args parse

    c = client.Collecter(config=config.CollectorConfiguration)
    time.sleep(5)

    #init logger
    warn_logger = get_logger("client_warn", config.CollectorConfiguration["ERROR_LOG_DIR"] + "python_main_err.log", level=logging.WARNING)
    info_logger = get_logger("client_info", config.CollectorConfiguration["LOG_DIR"] + "python_main.log", level=logging.INFO)
    #info_logger = get_logger("client_info", config.CollectorConfiguration["ERROR_LOG_DIR"][0]+"python_main.log", level=logging.INFO)

    # main thread report hashrate
    while True:
        try:
            c.report_handler()
        except Exception as e:
            #warn_logger.warning(e)
            warn_logger.exception(e)
            #info_logger.info(e)
            info_logger.exception(e)
        time.sleep(2)

if __name__ == "__main__":
    print("Oak main start ")
    main()