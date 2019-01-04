#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from handlers.base import BaseHandler

from model.account import Account

from libs.token import generate_token
from libs.standard_json_for_return import response_json
from libs.exceptions import MissingArgumentException, LoginFailException


class EditorHandler(BaseHandler):
    def post(self, *args, **kwargs):
        pass
