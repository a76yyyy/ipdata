# -*- encoding: utf-8 -*-
'''
@Description:  :默认配置
@Date          :2020/11/22 19:51:38
@Author        :a76yyyy
@version       :1.0
'''

import os

default_dat_update = True #执行ip_Sync.py时是否默认联网自动更新czipdata.dat文件, False为默认不更新, 不存在dat文件时该选项失效。
default_v6dat_update = False #执行ip_Sync.py时是否默认联网自动更新ipv6wry.db文件, False为默认不更新, 不存在dat文件时该选项失效。
default_sqlite3_update = True #当执行ip_Sync.py时是否默认自动更新SQLite3数据库, False为默认不更新。
default_txt_update = False #当数据文件版本无更新时是否默认自动更新czipdata.txt文件, False为默认不更新。
default_sql_update = True #当执行ip_Sync.py时是否默认自动更新数据库, False为默认不更新。
default_sql_export = False #当执行ip_Sync.py时是否默认自动导出sql脚本, False为默认不导出。
default_gz_export = True #当执行ip_Sync.py时是否默认自动导出sql脚本的gz压缩档, True为默认导出。
class mysql:
    host = "localhost"
    port = 3306
    user = "root"
    password = "123456"
    ip_database = "ipdata"
    charset = "utf8"
    connect_timeout = 3
    read_timeout = 5
    net_buffer_length = "1M"

class sqlite3:
    chdir=os.path.abspath(os.path.dirname(__file__)+os.path.sep+"data")
    ip_database=os.path.abspath(chdir+os.path.sep+"ipdata.db")

config = {
    'mysql':mysql,
    'sqlite3':sqlite3
}

try:
    from local_config import * # 修改local_config.py文件的内容不受通过git更新源码的影响
except ImportError:
    pass
