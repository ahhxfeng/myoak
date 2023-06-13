#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

# from oak_home import config
from oak_home.init_app import create_app
from oak_home.db import db

app = create_app("./config.py")
db.init_app(app=app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)