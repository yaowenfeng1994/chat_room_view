#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
base handler of tornado
"""
import os
import json
import time
import logging
import tornado.web
from pymysql.cursors import DictCursor
from pymysql.connections import Connection

from libs.token import ParseToken
from libs.mysql_db import MySQLConnectionPool
from libs.standard_json_for_return import response_json


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):

        super(BaseHandler, self).__init__(*args, **kwargs)

        is_production = True if (int(os.getenv("IS_PRODUCTION")) if os.getenv("IS_PRODUCTION") else 0) else False

        if is_production:
            database_setting = os.path.dirname(__file__) + "/../product_setting.json"
        else:
            database_setting = os.path.dirname(__file__) + "/../develop_setting.json"

        with open(database_setting) as ds:
            content = ds.read()
        try:
            data_obj = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            raise EnvironmentError("配置文件读取失败")

        # database 相关配置
        data_obj = data_obj.get("mysql").get("corgi")
        host = data_obj.get("host")
        user = data_obj.get("user")
        password = data_obj.get("password")
        database = data_obj.get("database")
        max_pool_size = data_obj.get("max_pool_size")
        # logging.info("database_info:"+str(data_obj))
        # auto_commit = database_setting.mysql.trading.auto_commit()

        self.dtx = None
        self.__token = None
        self.cursor = None
        self.mysql_connection = None
        self._auto_commit = True

        # 实例化数据库连接池
        self.mysql_connection_pool_trading = MySQLConnectionPool(
            "corgi",
            host=host,
            user=user,
            password=password,
            database=database,
            max_pool_size=max_pool_size
        )

    def prepare(self):
        # 租借数据库连接
        self.mysql_connection = self.mysql_connection_pool_trading.borrow_connection()
        try:
            assert isinstance(self.mysql_connection, Connection)

            # 根据配置文件开启/关闭自动提交
            self.mysql_connection.autocommit(self._auto_commit)

            # 实例化字典序游标
            self.cursor = self.mysql_connection.cursor(DictCursor)
        except AssertionError as err:
            logging.info(err)
            self.write(response_json(err_code=0x0201))
            self.finish()

    @property
    def token(self):
        """
        可以在该方法里直接获取用户信息，以及判断是否登录
        :return:
        """
        t1 = time.time()
        if not self.__token:
            self.__token = ParseToken(self)
            t2 = time.time()
            logging.info("ParseToken time:"+str(t2-t1))
            return self.__token
        else:
            return self.__token

    def data_received(self, chunk):
        super(BaseHandler, self).data_received(chunk=chunk)

    def on_finish(self):
        self.cursor.close()
        self.mysql_connection_pool_trading.return_connection(self.mysql_connection)
