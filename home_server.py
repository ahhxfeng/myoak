#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

import argparse
# from oak_home import config
from oak_home.init_app import create_app
from oak_home.init_db import db
from oak_home.logger import get_logger
from oak_home.models import *

app = create_app("./config.py")
db.init_app(app=app)

# command line to parser start and db operation
def command_line():
    parser = argparse.ArgumentParser(prog="home_server", description="the flask server ")
    Choices = ["runserver", "create_db", "drop_db"]
    parser.add_argument("command", type=str, choices=Choices)
    args = parser.parse_args()

    match args.command:
        case "runserver":
            # runserver 
            app.run(host="0.0.0.0", port=8080, debug=True)
        case "create_db":
            with app.app_context():
                db.create_all()
        case "drop_db":
            with app.app_context():
                db.drop_all()
        case _:
            print("bad command, please choose above{}".format(Choices))
       


if __name__ == "__main__":
    logger = get_logger("main_log", "main.log")
    command_line()