#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
token 生成及验证
"""

import time
import hmac
import json
import base64
import tornado.web

from model.account import Account


def generate_token(user_info: dict, key: str, expire: int=30):
    """
    用于生成token
    :param user_info: dict(用户信息字典)
    :param key: str("corgi_is_coming20180518")
    :param expire: int(最大有效时间,单位为s)
    :return:
    """
    time_str = str(time.time() + expire)
    time_byte = time_str.encode("utf-8")
    user_info_str = json.dumps(user_info)
    b64_user_info_str = str(base64.urlsafe_b64encode(user_info_str.encode("utf-8")), encoding="utf-8")
    sha1_time_hex_str = hmac.new(key.encode("utf-8"), time_byte, 'sha1').hexdigest()
    token = time_str + ':' + b64_user_info_str + ":" + sha1_time_hex_str
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def certify_token(key, token):
    """
    用于校验token以及提取token中的用户信息
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 3:
        return False, dict()
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        # token expired
        return False, dict()
    user_info = json.loads(base64.urlsafe_b64decode(bytes(token_list[1], encoding="utf-8")).decode('utf-8'))
    known_sha1_str = token_list[2]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_str = sha1.hexdigest()
    if calc_sha1_str != known_sha1_str:
        # token certification failed
        return False, dict
    # token certification success
    return True, user_info


class ParseToken(object):

    def token_exists_in_db(self):

        cursor = Account(self.cursor)
        result = cursor.fetch_token(token=self.__token)
        if result:
            return True
        else:
            return False

    def __init__(self, that):
        self.cursor = that.cursor
        self.__is_login = 0
        self.__token = ""
        self.__user_id = 0
        self.__nickname = ""
        self.__sex = 1
        self.__mobile = ""
        self.__email = ""
        self.__is_staff = 0
        # token是否过期或者失效
        self.__token_expire = True

        assert isinstance(that, tornado.web.RequestHandler) is True

        self.__token = that.get_cookie("token")
        if self.token_exists_in_db():
            boolean, user_info = certify_token(key="corgi_is_coming20180518", token=self.__token)
            if boolean:
                self.__is_login = 1
                self.__user_id = int(user_info.get("user_id"))
                if user_info.get("nickname"):
                    self.__nickname = user_info.get("nickname")
                if user_info.get("sex"):
                    self.__sex = int(user_info.get("sex"))
                if user_info.get("mobile"):
                    self.__mobile = user_info.get("mobile")
                if user_info.get("email"):
                    self.__email = user_info.get("email")
                if user_info.get("is_staff"):
                    self.__is_staff = int(user_info.get("is_staff"))
                self.__token_expire = False

    @property
    def token_expire(self):
        return self.__token_expire

    @property
    def token(self):
        return self.__token

    @property
    def user_id(self):
        return self.__user_id

    @property
    def nickname(self):
        return self.__nickname

    @property
    def sex(self):
        return self.__sex

    @property
    def mobile(self):
        return self.__mobile

    @property
    def email(self):
        return self.__email

    @property
    def is_staff(self):
        return self.__is_staff

    @property
    def is_login(self):
        return self.__is_login

# if __name__ == '__main__':
#     key1 = "corgi_is_coming20180518"
#     user_info1 = {"account": 60000, "mobile": 123456, "email": "60000@qq.com"}
#     # 一小时后过期
#     token1 = generate_token(user_info1, key1, 50)
#     print(len(token1), token1)
#     result = certify_token(key1, token1)
#     print(result)

