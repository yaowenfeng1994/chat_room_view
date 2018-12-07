#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
自定义异常处理
"""

import json
from libs.error_message import err


class BaseError(Exception):
    """
    自定义异常基类
    """
    def __init__(self,
                 err_code,
                 err_msg=None,
                 err_msg_en=None):

        super(BaseError, self).__init__()
        try:
            self.err_code = int(err_code)
        except ValueError:
            raise InvalidCodeException

        default_msg = err[self.err_code]
        if default_msg is None:
            raise NotDefinedException

        self.err_msg = default_msg[0] + ", " + err_msg if err_msg else default_msg[0] if default_msg[0] else "未知错误代码"
        self.err_msg_en = err_msg_en if err_msg_en else default_msg[1] if default_msg[1] else "unknown error code"

        # self.debug_mode = DEBUG_MODE if debug_mode is None else bool(debug_mode)
        # self._pid = CUR_PID
        # self._trace = None

    def __str__(self):

        return json.dumps({
            "err_code": self.err_code,
            "err_msg": self.err_msg,
            "err_msg_en": self.err_msg_en}, ensure_ascii=False, indent=4, sort_keys=True)


class InvalidCodeException(Exception):
    """
    异常::错误的异常代码
    """
    pass


class UnknownErrorException(BaseError):
    """
    异常::未知错误
    """

    def __init__(self):
        super(UnknownErrorException, self).__init__(err_code=0x0001)


class NotDefinedException(BaseError):
    """
    异常::该异常未被定义
    """

    def __init__(self):
        super(NotDefinedException, self).__init__(err_code=0x0002)


class MissingArgumentException(BaseError):
    """
    异常::请求缺少参数
    """

    def __init__(self):
        super(MissingArgumentException, self).__init__(err_code=0x0003)


class PasswordDiffException(BaseError):
    """
    异常::两次输入密码不同
    """

    def __init__(self):
        super(PasswordDiffException, self).__init__(err_code=0x0101)


class CreateAccountFailException(BaseError):
    """
    异常::创建用户失败
    """

    def __init__(self):
        super(CreateAccountFailException, self).__init__(err_code=0x0102)


class LoginFailException(BaseError):
    """
    异常::登录失败,登陆密码错误或者账号不存在等原因
    """

    def __init__(self, err_msg=None, err_msg_en=None):
        super(LoginFailException, self).__init__(err_code=0x0103, err_msg=err_msg, err_msg_en=err_msg_en)


class PoolIsFullException(BaseError):
    """
    异常::连接池已满
    """

    def __init__(self):
        super(PoolIsFullException, self).__init__(err_code=0x0202)


class PoolIsEmptyException(BaseError):
    """
    异常::连接池已空
    """

    def __init__(self):
        super(PoolIsEmptyException, self).__init__(err_code=0x0203)
