#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
数据库连接池模块
"""

import logging
import threading
import contextlib

from pymysql.connections import Connection
from pymysql.cursors import DictCursor, Cursor

from libs.mysql_pool import PoolContainer
from libs.exceptions import PoolIsFullException, PoolIsEmptyException


def singleton(cls):
    """
    单例模式装饰器
    :param cls: 被装饰类对象, Logger.
    :return: <closure>.
    """

    instances = {}

    def _singleton(name, **kwargs):
        if cls not in instances:
            instances[cls] = {name: cls(name, **kwargs)}
        else:
            if name not in instances[cls]:
                instances[cls][name] = cls(name, **kwargs)
        print(instances)
        return instances[cls][name]

    return _singleton


@singleton
class MySQLConnectionPool(object):
    """
    连接池管理器
    """

    def __init__(self,
                 pool_name,
                 host=None,
                 user=None,
                 password="",
                 database=None,
                 port=3306,
                 charset="utf8mb4",
                 use_dict_cursor=True,
                 max_pool_size=30,
                 enable_auto_resize=True,
                 auto_resize_scale=1.5,
                 pool_resize_boundary=48,
                 defer_connect_pool=False,
                 **kwargs):

        """
        连接池初始化方法 (oﾟvﾟ)ノ 明白吗？
        :param pool_name: <str>, 连接池名称, 用以区分连接池实例
        :param host: <str>, 数据库host
        :param user: <str>, 数据库用户名
        :param password: <str>, 数据库密码
        :param database: <str>, 默认数据库schema(可选)
        :param port: <int>, 数据库端口号, 默认3306
        :param charset: <str>, 数据库字符集, 默认utf8mb4
        :param use_dict_cursor: <boolean>, 是否使用DictCursor
        :param max_pool_size: <int>, 最大连接池大小
        :param enable_auto_resize: <boolean>, 开启连接池大小动态调整功能
        :param pool_resize_boundary: <int>, 数据库连接数大小边界
        :param auto_resize_scale:  <float>, 数据库连接池动态调整倍率
        :param defer_connect_pool: <boolean>, 构造时不连接数据库, 默认关闭
        :param kwargs: 其他传递给 `pymysql.Connection` 的参数
        """

        # 数据库连接配置
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._charset = charset
        self._cursor_class = DictCursor if use_dict_cursor else Cursor
        self._other_kwargs = kwargs

        # 连接池配置
        self._pool_name = pool_name
        self._max_pool_size = max_pool_size if max_pool_size < pool_resize_boundary else pool_resize_boundary

        self._enable_auto_resize = enable_auto_resize
        self._pool_resize_boundary = pool_resize_boundary
        if auto_resize_scale < 1:
            raise ValueError(
                "非法的调整倍率 {}, 必须大于1".format(auto_resize_scale))

        self._auto_resize_scale = int(round(auto_resize_scale, 0))
        self._pool_container = PoolContainer(self._max_pool_size)

        self.__safe_lock = threading.RLock()
        self.__is_killed = False
        self.__is_connected = False

        self.logger = logging.getLogger("pymysql_pool")

        if not defer_connect_pool:
            self.connect()

    def __repr__(self):

        return "<MySQLConnectionPool name={!r}, size={!r}>".format(self.pool_name, self.size)

    def __del__(self):

        self.close()

    def __iter__(self):

        return iter(self._pool_container)

    @property
    def pool_name(self):
        """
        连接池名称
        :return:
        """

        return self._pool_name

    @property
    def pool_size(self):
        """
        连接池大小
        :return:
        """

        return self._pool_container.pool_size

    @property
    def free_size(self):
        """
        空闲池大小
        :return:
        """

        return self._pool_container.free_size

    @property
    def size(self):
        """
        连接池总大小
        :return:
        """

        return "<boundary={}, max={}, current={}, free={}>".format(self._pool_resize_boundary,
                                                                   self._max_pool_size,
                                                                   self.pool_size,
                                                                   self.free_size)

    @contextlib.contextmanager
    def cursor(self, cursor=None):
        """
        获取游标对象的快捷方法
        不要多次重复获取, 会导致性能问题, 建议还是用下面的connection方法
        """

        with self.connection(True) as conn:
            assert isinstance(conn, Connection)
            cursor = conn.cursor(cursor)

            try:
                yield cursor
            except Exception as err:
                conn.rollback()
                raise err
            finally:
                cursor.close()

    @contextlib.contextmanager
    def connection(self, autocommit=True):
        """
        从连接池中获取新的连接
        :param autocommit:
        :return:
        """

        conn = self.borrow_connection()
        assert isinstance(conn, Connection)
        old_value = conn.get_autocommit()
        conn.autocommit(autocommit)

        try:
            yield conn
        except Exception as err:
            # self.logger.error(str(err))
            raise err
        finally:
            conn.autocommit(old_value)
            self.return_connection(conn)

    def connect(self):
        """
        连接池初始化连接数据库方法
        :return:
        """

        if self.__is_connected:
            return

        self.logger.info("[{}] 接入连接池".format(self))

        test_conn = self._create_connection()
        try:
            test_conn.ping()
        except Exception as err:
            raise err
        else:
            with self.__safe_lock:
                self.__is_connected = True

            self._adjust_connection_pool()
        finally:
            test_conn.close()

    def close(self):
        """
        关闭连接池
        :return:
        """

        self.logger.info("[{}] 关闭连接池".format(self))

        with self.__safe_lock:
            if self.__is_killed is True:
                return True

        self._free()

        with self.__safe_lock:
            self.__is_killed = True

    def borrow_connection(self):
        """
        从连接池中租借连接
        :return:
        """

        block = False

        while True:
            conn = self._borrow(block)
            if conn is None:
                block = not self._adjust_connection_pool()
            else:
                return conn

    def _borrow(self, block):
        """
        租借连接 shadow 方法
        :param block:
        :return:
        """

        try:
            connection = self._pool_container.get(block, None)
        except PoolIsEmptyException:
            return None
        else:
            connection.ping(reconnect=True)
            return connection

    def return_connection(self, connection):
        """
        获取连接
        :param connection:
        :return:
        """

        return self._pool_container.return_(connection)

    def _adjust_connection_pool(self):
        """
        自适应调整连接池大小
        :return:
        """

        self.logger.debug("[{}] 调整连接池大小, 当前大小是 '{}'".format(self, self.size))

        if self.pool_size >= self._max_pool_size:
            if self._enable_auto_resize:
                self._adjust_max_pool_size()

        try:
            connection = self._create_connection()
        except Exception as err:
            self.logger.error(err)
            return False
        else:
            try:
                self._pool_container.add(connection)
            except PoolIsFullException:
                return False
            else:
                return True

    def _adjust_max_pool_size(self):
        """
        自适应调整连接池大小 shadow 方法
        :return:
        """

        with self.__safe_lock:
            self._max_pool_size *= self._auto_resize_scale
            if self._max_pool_size > self._pool_resize_boundary:
                self._max_pool_size = self._pool_resize_boundary
            self.logger.debug("[{}] 连接池最大连接数调整至 {}".format(self, self._max_pool_size))
            self._pool_container.max_pool_size = self._max_pool_size

    def _free(self):
        """
        释放连接池资源
        :return:
        """

        for connection in self:
            try:
                connection.close()
            except Exception as err:
                _ = err

    def _create_connection(self):
        """
        初始化连接池数据库连接
        :return:
        """

        return Connection(host=self._host,
                          user=self._user,
                          password=self._password,
                          database=self._database,
                          port=self._port,
                          charset=self._charset,
                          cursorclass=self._cursor_class,
                          **self._other_kwargs)
