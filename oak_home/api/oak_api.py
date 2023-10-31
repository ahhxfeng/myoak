# coding=utf-8

from flask_restful import Api

"""
A golbal restful api in the oak application by using flask_restful
"""

class OakException(Exception):
    http_code = 500
    err_code = 1
    err_message = "unknown mistake"

    def __init__(self, err_code, err_message, http_code=500) -> None:
        self.http_code = http_code
        self.err_code = err_code
        self.err_message = err_message

class OakApi(Api):
    def handle_err(self, e):

        import traceback

        if isinstance(e, OakException):
            http_code = e.http_code
            err_code = e.err_code
            err_message = e.err_message
        # elif isinstance(e, )
        else:
            http_code = getattr(e, "code", 500)
            err_code = 110
            err_message = str(e)

        print('----------------')
        print('Resetful error: ' + err_message)
        print(traceback.format_exc())
        response = {
            'code': err_code,
            'message': err_message,
            'data': None,
        }
        return self.make_response(response, http_code)
