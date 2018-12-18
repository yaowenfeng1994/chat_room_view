#! -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.web
from tornado.options import define, options
import os

define("port", default="8080", help="run on the given port", type=int)
define("sql_debug", default=False, type=bool)

settings = dict(
    # xsrf_cookies=True,
    # cookie_secret="RYxFqFQyRCiCZ/nxFfTMCrbqZpRZ5UW9tQ86fKvrfIw=",
    login_url="/login",
    # debug=options.debug,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    # 静态文件
    static_path=os.path.join(os.path.dirname(__file__), "static"),
)

url = [
    # 获取产品信息
    (r"^/v1/register",
     "handlers.account.register.RegisterHandler"),
]


class Application(tornado.web.Application):
    def __init__(self):
        super(Application, self).__init__(url, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    print("service start... %s" % options.port)
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
