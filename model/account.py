#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号创建删除等操作
"""
import time
import logging

from pymysql.err import IntegrityError


class Account(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def create_account(self, account, password):
        sql1 = """
          SELECT 
          t1.id AS user_id 
          FROM corgi.user t1
          WHERE t1.account = %s
        """
        self.cursor.execute(sql1, (str(account)))
        user = self.cursor.fetchone()
        if user:
            return False

        sql2 = "INSERT INTO corgi.`user` (account, password, is_staff, create_time) VALUES (%s, %s, 0, %s);"
        try:
            self.cursor.execute(sql2, (str(account), str(password), int(time.time())))
            return True
        except IntegrityError as err:
            logging.info(err)
            return False

    def fetch_password(self, account):
        sql = "SELECT `password` FROM corgi.user WHERE account = %s"
        self.cursor.execute(sql, (str(account)))
        result = self.cursor.fetchone()
        if result:
            password = result.get("password")
        else:
            password = 0
        return password

    def fetch_user_info(self, account):
        sql = """
          SELECT 
          t1.id AS user_id, nickname, sex, mobile, email, is_staff, t1.account  
          FROM corgi.user t1
          LEFT JOIN corgi.user_info t2
          ON t1.id = t2.user_id
          WHERE t1.account = %s
        """
        self.cursor.execute(sql, (str(account)))
        user_info = self.cursor.fetchone()
        return user_info

    def fetch_token(self, token):
        sql1 = "SELECT token FROM corgi.token WHERE token = %s"
        self.cursor.execute(sql1, (str(token)))
        token_result = self.cursor.fetchone()
        if token_result:
            return True
        else:
            return False

    def create_token(self, user_id, token):
        sql1 = "SELECT token FROM corgi.token WHERE user_id = %s"
        self.cursor.execute(sql1, (str(user_id)))
        token_result = self.cursor.fetchone()
        if token_result:
            sql2 = " UPDATE corgi.token SET token = %s, create_time = %s WHERE user_id = %s"
            self.cursor.execute(sql2, (str(token), int(time.time()), str(user_id)))
            return True
        else:
            sql3 = "INSERT INTO corgi.token ( user_id, token, create_time) VALUES (%s, %s, %s)"
            try:
                self.cursor.execute(sql3, (str(user_id), str(token), int(time.time())))
                return True
            except IntegrityError as err:
                logging.info(err)
                return False
