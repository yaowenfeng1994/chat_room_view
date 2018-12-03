#! -*- coding:utf-8 -*-

import tornado.web


class LoginHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write("hello")
