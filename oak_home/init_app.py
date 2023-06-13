#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

from flask import Flask

from . import config

# create app for later use
def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    return app