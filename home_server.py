#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

# from oak_home import config
from oak_home.init_app import create_app
from oak_home.init_db import db
from oak_home.logger import get_logger

app = create_app("./config.py")
db.init_app(app=app)


if __name__ == "__main__":
    logger = get_logger("main_log", "main.log")
    with app.app_context():
        logger.info("try to create all tables")
        # print(app.config)
        from oak_home.models import *
        
        db.create_all()
        # db.drop_all()
        logger.info("create tables done")
    app.run(host="0.0.0.0", port=8080, debug=True)