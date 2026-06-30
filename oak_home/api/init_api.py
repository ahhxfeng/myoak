#coding=utf-8

from .oak_api import OakApi

def bind_api(app):
    """
    init api with the given flask app
    """
    Api = OakApi(app)
    return Api
