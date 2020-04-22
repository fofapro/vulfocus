# coding:utf-8


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "code": 20000,
        "data": {
            "token": token
            }
        }
