#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
错误信息集合
"""

err = {
    # 0x00 为系统内存错误
    0x0000: ["请求成功", "success"],
    0x0001: ["未知错误", "unknown error"],
    0x0002: ["方法或对象未实现", "method or object not implemented"],
    0x0003: ["请求参数缺失", "missing request parameter"],

    # 0x01 为账号方面异常
    0x0101: ["两次输入密码不同", "two passwords are different"],
    0x0102: ["创建账号失败,该账号已经存在", "failed to create account"],
    0x0103: ["登录失败", "logon failure"],

    # 0x02 为数据库连接异常
    0x0201: ["连接丢失", "connection is lost"],
    0x0202: ["连接池已满", "pool is full"],
    0x0203: ["连接池已空", "pool is empty"]
}
