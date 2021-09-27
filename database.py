# -*- encoding: utf-8 -*-
'''
@Description:  :数据库处理脚本
@Date          :2020/10/08 20:22:08
@Author        :a76yyyy
@version       :1.0
'''
import pymysql
import sqlite3
import os
from configs import mysql
from func_timeout import func_set_timeout,exceptions
import sys

class mysql_Database:
    host = mysql.host
    port = mysql.port
    user = mysql.user
    password = mysql.password
    charset = mysql.charset

    def __init__(self,*args):
        if len(args) == 1:
            self.db = args[0]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset)
        elif len(args) == 2:
            self.db = args[0]
            self.connect_timeout = args[1]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset, connect_timeout=self.connect_timeout)
        elif len(args) == 3:
            self.db = args[0]
            self.connect_timeout = args[1]
            self.read_timeout = args[2]
            self.connection = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, charset=self.charset, connect_timeout=self.connect_timeout, read_timeout=self.read_timeout)
        else:
            print('参数输入错误')
            sys.exit()
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def execute(self,code):
        try:
            self.cursor.execute(code)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def executemany(self,code,slist):
        try:
            self.cursor.executemany(code,slist)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def query(self, query, *args):
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)# 得到一个可以执行SQL语句并且将结果作为字典返回的游标
        result = None
        timeout = None
        if args:
            if len(args) == 1:
                timeout = args[0]
        if timeout:
            @func_set_timeout(timeout)
            def timelimited():
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                return result
            try:
                result = timelimited()
            except exceptions.FunctionTimedOut:
                print("timeout!")
                self.cursor.close()
                return result
        else:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.connection.close()

class sqlite3_Database:
    
    def __init__(self,db_file,connect_timeout=5.0):
        self.connection = sqlite3.connect(db_file,timeout=connect_timeout)
        self.cursor = self.connection.cursor()

    def insert(self, query, params):
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def execute(self,code):
        try:
            self.cursor.execute(code)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    def executemany(self,code,slist):
        try:
            self.cursor.executemany(code,slist)
            self.connection.commit()
        except Exception as e:
            print(e)
            self.connection.rollback()
    @staticmethod
    def dictFactory(cursor,row):
        """将sql查询结果整理成字典形式"""
        d={}
        for index,col in enumerate(cursor.description):
            d[col[0]]=row[index]
        return d
    def query(self, query, *args):
        self.connection.row_factory=self.dictFactory # 得到一个可以执行SQL语句并且将结果作为字典返回的游标
        self.cursor = self.connection.cursor()
        result = None
        timeout = None
        if args:
            if len(args) == 1:
                timeout = args[0]
        if timeout:
            @func_set_timeout(timeout)
            def timelimited():
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                return result
            try:
                result = timelimited()
            except exceptions.FunctionTimedOut:
                print("timeout!")
                self.cursor.close()
                return result
        else:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
        return result

    def __del__(self):
        self.connection.close()