from random import choice
import random
import smtplib
import logging
import time
from email.mime.text import MIMEText
import dns.resolver

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

def generate_code(code_length=10):
    """生成验证码函数
    :param code_length:验证码长度
    :return:code"""
    seed="0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz"
    code=""
    for i in range(code_length):
        code+=choice(seed)
    return code

def fetch_mx(host):
    '''
    解析服务邮箱
    :param host:
    :return:
    '''
    answers = dns.resolver.resolve(host, 'MX')
    res = [str(rdata.exchange) for rdata in answers]
    return res


def validate_email(email):
    try:
        name, host = email.split("@")
        host = random.choice(fetch_mx(host))
        s = smtplib.SMTP(host, timeout=10)
        helo = s.docmd('HELO chacuo.net')
        send_from = s.docmd('MAIL FROM:<3121113@chacuo.net>')
        send_from = s.docmd('RCPT TO:<%s>' % email)
        s.close()
        if send_from[0] == 250 or send_from[0] == 451:
            return True
        elif send_from[0] == 550:
            return False
    except Exception as e:
        return None
    return None