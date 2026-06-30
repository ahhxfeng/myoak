#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

from flask import Flask

from . import config
from .logger import get_logger

# create app for later use
def create_app(config_file):
    oak_home = get_logger("oak-home", "oak-home.log")
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = config.APP_FLASK_KEY
    # oak_home.warning("waring!!! for test")
    oak_home.info("try to log someting",exc_info=1)
    oak_home.info("try to log some useful information")
    oak_home.info(app.config)
    

    return app
