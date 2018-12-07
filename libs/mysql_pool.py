#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
连接池对象模块
"""

import logging
import threading
from queue import Queue, Empty

from libs.exceptions import PoolIsFullException, PoolIsEmptyException

__all__ = ["PoolContainer", "PoolIsEmptyException", "PoolIsFullException"]


class PoolContainer(object):
    """
    连接池类
    """

    def __init__(self, max_pool_size=0):
        self.logger = logging.getLogger("pymysql_pool")
        self._pool_lock = threading.RLock()
        self._free_items = Queue()
        self._pool_items = set()
        self._max_pool_size = 0
        self.max_pool_size = max_pool_size

    def __repr__(self):
        return "<{0.__class__.__name__} {0.size})>".format(self)

    def __iter__(self):
        with self._pool_lock:
            return iter(self._pool_items)

    def __contains__(self, item):
        with self._pool_lock:
            return item in self._pool_items

    def __len__(self):
        with self._pool_lock:
            return len(self._pool_items)

    def add(self, item):
        """增加新连接至连接池"""

        if item is None:
            return None

        if item in self:
            self.logger.debug(
                "连接对象重复 '{}', "
                "当前连接池大小为 '{}'".format(item, self.size))
            return None

        if self.pool_size >= self.max_pool_size:
            raise PoolIsFullException()

        self._free_items.put_nowait(item)
        with self._pool_lock:
            # self._pool_items.append(item)
            self._pool_items.add(item)

        self.logger.debug(
            "增加连接对象成功 '{!r}', "
            "当前连接池大小为 '{}'".format(item, self.size))

    def return_(self, item):
        """
        归还连接对象, 该连接对象必须已经存在于连接池之中
        :param item: <obj>, 连接对象
        """

        if item is None:
            return False

        if item not in self:
            self.logger.error(
                "当前连接池中并无该连接对象: '{}'".format(item))
            return False

        self._free_items.put_nowait(item)
        self.logger.debug("归还连接成功 '{!r}', 当前连接池大小为 '{}'".format(item, self.size))
        return True

    def get(self, block=True, wait_timeout=60):
        """
        从连接池中获取连接, 若无连接可用, block for wait_timeout
        :param block: <boolean>, 是否阻塞
        :param wait_timeout: <int>, 阻塞等待时长
        """

        try:
            item = self._free_items.get(block, timeout=wait_timeout)
        except Empty:
            raise PoolIsEmptyException
        else:
            self.logger.debug("获取连接 '{}', 当前连接池大小为 '{}'".format(item, self.size))
            return item

    @property
    def size(self):
        """
        连接池总大小
        :return:
        """

        return "<最大={}, 当前={}, 空闲={}>".format(self.max_pool_size, self.pool_size, self.free_size)

    @property
    def max_pool_size(self):
        """
        最大连接池大小
        :return:
        """

        return self._max_pool_size

    @max_pool_size.setter
    def max_pool_size(self, value):
        """
        设置最大连接池大小
        :param value:
        :return:
        """

        if value > self._max_pool_size:
            self._max_pool_size = value

    @property
    def pool_size(self):
        """
        连接池总大小
        :return:
        """

        return len(self)

    @property
    def free_size(self):
        """
        诶呀, 与 queue 模块中描述的不同
        """

        return self._free_items.qsize()
