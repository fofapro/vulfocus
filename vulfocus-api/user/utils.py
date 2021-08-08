from random import choice

def jwt_response_payload_handler(token, user=None, request=None):   # 如果不知道为啥要带这三个参数，可以ctrl+shift+f全局搜索，再jwt得post方法有
    """
    自定义jwt认证成功返回对象
    :param token: token
    :param user: 用户对象
    :param request:
    :return: 用户token,id,户名username,用户头像
    """
    return {
        "id": user.id,
        "username": user.username,
        "token": token,
    }

def generate_code(code_length=4):
    """生成验证码函数
    :param code_length:验证码长度
    :return:code"""
    seed="0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"
    code=""
    for i in range(code_length):
        code+=choice(seed)
    return code