#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from handlers.base import BaseHandler

from model.account import Account

from libs.token import generate_token
from libs.standard_json_for_return import response_json
from libs.exceptions import MissingArgumentException, LoginFailException


class LoginHandler(BaseHandler):

    def post(self, *args, **kwargs):

        if isinstance(self.request.body, bytes):
            extract_data = json.loads(self.request.body.decode("utf-8"))
        else:
            extract_data = json.loads(self.request.body)
        request_data = extract_data.get("data")
        try:
            account = request_data.get("account")
            password = request_data.get("password")
            if not account or not password:
                raise MissingArgumentException

            cursor = Account(self.cursor)
            correct_password = cursor.fetch_password(account=account)
            if correct_password == password:
                # 发放token并保存到数据库
                corgi_key = "corgi_is_coming20180518"
                user_info = cursor.fetch_user_info(account=account)
                token = generate_token(user_info=user_info, key=corgi_key)
                token_result = cursor.create_token(user_id=user_info.get("user_id"), token=token)
                if not token_result:
                    raise LoginFailException(err_msg="创建token失败",
                                             err_msg_en="create token failure")
                data = {"token": token}
                self.write(response_json(
                    err_code=0x0000, data=data
                ))
                self.finish()
                return
            else:
                raise LoginFailException(err_msg="登陆密码错误或者账号不存在",
                                         err_msg_en="login password error or account does not exist")

        except (MissingArgumentException, LoginFailException) as why:
            data = {"token": ""}
            self.write(response_json(
                err_code=why.err_code,
                err_msg=why.err_msg,
                err_msg_en=why.err_msg_en,
                data=data
            ))
            self.finish()
            return
