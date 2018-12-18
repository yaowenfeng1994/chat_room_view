#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from handlers.base import BaseHandler

from model.account import Account

from libs.standard_json_for_return import response_json
from libs.exceptions import MissingArgumentException, PasswordDiffException, CreateAccountFailException


class RegisterHandler(BaseHandler):

    def get(self, *args, **kwargs):
        self.render("register.html")

    def post(self, *args, **kwargs):
        # if isinstance(self.request.body, bytes):
        #     extract_data = json.loads(self.request.body.decode("utf-8"))
        # else:
        #     extract_data = json.loads(self.request.body)
        # request_data = extract_data.get("data")
        try:
            # account = request_data.get("account")
            # password = request_data.get("password")
            # confirm_password = request_data.get("confirm_password")
            account = self.get_argument("r_account")
            password = self.get_argument("r_password")
            confirm_password = self.get_argument("r_confirm_password")
            print(account, password, confirm_password)
            # if not account or not password or not confirm_password:
            #     raise MissingArgumentException
            # elif confirm_password != password:
            #     raise PasswordDiffException
            #
            # cursor = Account(self.cursor)
            # result = cursor.create_account(account=account, password=password)
            # if result:
            #     self.write(response_json(
            #         err_code=0x0000, data={}
            #     ))
            #     self.finish()
            #     return
            # else:
            #     raise CreateAccountFailException

        except (MissingArgumentException, PasswordDiffException, CreateAccountFailException) as why:
            self.write(response_json(
                err_code=why.err_code,
                err_msg=why.err_msg,
                err_msg_en=why.err_msg_en
            ))
            self.finish()
            return
