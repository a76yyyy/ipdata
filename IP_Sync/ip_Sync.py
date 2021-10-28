# -*- encoding: utf-8 -*-
'''
@Description:  :实现纯真IP数据库和ZXinc_IPv6数据库的下载和更新.
@Date          :2020/06/25 12:00:05
@Author        :a76yyyy
@version       :2.0
'''

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import ipUpdate
import ipv6Update
from ipSearch import IPLoader,IPv6Loader
from dat2txt import get_ip_info,get_ipv6_info
from database import mysql_Database, sqlite3_Database
from configs import config,default_dat_update,default_sqlite3_update,default_txt_update,default_sql_update,default_sql_export,default_gz_export
from dat2mysql import dat2mysql,db2mysql
from dat2sqlite3 import dat2sqlite3,db2sqlite3
from collegeUpdate import collegeUpdate
from convert import convert
from file_set import file_set
from __init__ import data_dir,tmp_dir,DEFAULT_FILE_LOCATION,sql_file,table_college_info_sql_file,table_iprange_info_sql_file,table_ipv6_range_info_sql_file
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

file_set(tmp_dir,'dir')
file_set(data_dir,'dir')

def down(filename= None,version_file= None):
    """
    @description  :从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名.
    ---------
    @param  :filename : 输出纯真IP数据库的dat文件名或路径,默认为"../data/czipdata.dat".
    -------
    @Returns  :None
    -------
    """

    if filename is None:
        filename =  os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
    if version_file is None:
        version_file = os.path.abspath(data_dir+os.path.sep+"czipdata_version.bin")
    return ipUpdate.dat_down_info(filename,version_file)


def dat2Txt(dat_filename= None, txt_filename= None, startIndex= None, endIndex= None):
    """
    @description  :将纯真IP数据库的dat文件转换为txt文本文件
    ---------
    @params  :dat_filename : 纯真IP数据库的dat文件名或路径,默认为"../data/czipdata.dat"
             txt_filename : 输出文本文件的文件名或路径,默认为"../data/czipdata.txt"
             startIndex : 起始索引, 默认为0
             endIndex : 结束索引, 默认为IP数据库总记录数
    -------
    @Returns  :None
    -------
    """

    if dat_filename is None:
        dat_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
    if not file_set(dat_filename) or default_dat_update:
        tag = down(dat_filename)
    q = IPLoader(dat_filename)
    if txt_filename is None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
    if startIndex is None:
        startIndex = 0
    if endIndex is None:
        endIndex = q.idx_count
    if tag or default_txt_update:
        file_set(txt_filename)
        get_ip_info(dat_filename,txt_filename,startIndex,endIndex)
        return tag

def v6down(filename= None,version_file= None, ipv4update=False):
    """
    @description  :从ZXinc(ip.zxinc.org)导入ipv6wry.db至指定dat格式文件名.
    ---------
    @param  :filename : 输出IPv6数据库的db件名或路径,默认为"../data/ipv6data.db".
    -------
    @Returns  :None
    -------
    """

    if filename is None:
        filename =  DEFAULT_FILE_LOCATION
    if version_file is None:
        version_file = os.path.abspath(data_dir+os.path.sep+"ipv6data_version.bin")
    return ipv6Update.db_down_info(filename,version_file,ipv4update)

def db2Txt(db_filename= None, txt_filename= None, startIndex= None, endIndex= None, ipv4update=False):
    """
    @description  :将ZXinc_IPv6数据库的db文件转换为txt文本文件
    ---------
    @params  :db_filename : ZXinc_IPv6数据库的db文件名或路径,默认为"../data/ipv6data.dat"
             txt_filename : 输出文本文件的文件名或路径,默认为"../data/ipv6data.txt"
             startIndex : 起始索引, 默认为0
             endIndex : 结束索引, 默认为IPv6数据库总记录数
    -------
    @Returns  :None
    -------
    """

    if db_filename is None:
        db_filename = DEFAULT_FILE_LOCATION
    if not file_set(db_filename) or default_dat_update:
        tag = v6down(db_filename,ipv4update=ipv4update)
    D = IPv6Loader(db_filename)
    if txt_filename is None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"ipv6data.txt")
    if startIndex is None:
        startIndex = 0
    if endIndex is None:
        endIndex = D.count
    if tag or default_txt_update:
        file_set(txt_filename)
        get_ipv6_info(db_filename,txt_filename,startIndex,endIndex)
        return tag

def dat2Mysql(mysql_object,ip_tablename= None, txt_filename= None):
    """
    @description  :将纯真IP数据库的txt文件转换至mysql数据库指定表中
    ---------
    @params  :ip_tablename : mySQL中IP数据库的表名,默认为"iprange_info"
             txt_filename : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"
    -------
    @Returns  :None
    -------
    """
    
    if txt_filename is None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        if not file_set(txt_filename):
            dat2Txt(txt_filename= txt_filename)
    if ip_tablename is None:
        ip_tablename = 'iprange_info'
    mysql = mysql_object
    dat2mysql(mysql,ip_tablename,txt_filename)

def db2Mysql(mysql_object,ipv6_tablename= None, db_filename= None,ipv6update= True):
    """
    @description  :将ZXinc_IPv6数据库的db文件转换至mysql数据库指定表中
    ---------
    @params  :ipv6_tablename : mySQL中IP数据库的表名,默认为"ipv6_range_info"
             db_filename : 输入文本文件的文件名或路径,默认为"../data/ipv6data.db"
    -------
    @Returns  :None
    -------
    """
    
    if db_filename is None:
        db_filename = DEFAULT_FILE_LOCATION
        if not file_set(db_filename):
            v6down(db_filename)
    if ipv6_tablename is None:
        ipv6_tablename = 'ipv6_range_info'
    mysql = mysql_object
    if ipv6update:
        db2mysql(mysql,ipv6_tablename,db_filename)

def dat2SQLite3(sqlite3_object,ip_tablename= None, txt_filename= None):
    """
    @description  :将纯真IP数据库的txt文件转换至sqlite3数据库指定表中
    ---------
    @params  :ip_tablename : sqlite3中IP数据库的表名,默认为"iprange_info"
             txt_filename : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"
    -------
    @Returns  :None
    -------
    """
    
    if txt_filename is None:
        txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
        if not file_set(txt_filename):
            dat2Txt(txt_filename= txt_filename)
    if ip_tablename is None:
        ip_tablename = 'iprange_info'
    sqlite3 = sqlite3_object
    dat2sqlite3(sqlite3,ip_tablename,txt_filename)

def db2SQLite3(sqlite3_object,ipv6_tablename= None, db_filename= None,ipv6update= True):
    """
    @description  :将ZXinc_IPv6数据库的db文件转换至sqlite3数据库指定表中
    ---------
    @params  :ipv6_tablename : sqlite3中IP数据库的表名,默认为"ipv6_range_info"
             db_filename : 输入文本文件的文件名或路径,默认为"../data/ipv6data.db"
    -------
    @Returns  :None
    -------
    """
    
    if db_filename is None:
        db_filename = DEFAULT_FILE_LOCATION
        if not file_set(db_filename):
            v6down(db_filename)
    if ipv6_tablename is None:
        ipv6_tablename = 'ipv6_range_info'
    sqlite3 = sqlite3_object
    if ipv6update:
        db2sqlite3(sqlite3,ipv6_tablename,db_filename)

def collegeupdate(collegeJson= None, college_tablename= None, sqlite3file= None):
    """
    @description  :从'https://github.com/pg7go/The-Location-Data-of-Schools-in-China'导入'大学-8084.json'至指定json格式文件名.
    ---------
    @param  :collegeJson : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             college_tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info"
             sqlite3file : sqlite3数据库文件名或路径，默认为"../data/ipdata.db".
    -------
    @Returns  :None
    -------
    """
    
    if collegeJson is None:
        collegeJson =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if college_tablename is None:
        college_tablename = 'college_info'
    collegeUpdate(filename, college_tablename, sqlite3file=sqlite3file)

def convertipv4(sql_object,college_tablename= None,num_config= None,start_id= None,college_filename= None,correct_filename= None,sqlite3file= None):
    """
    @description :将纯真IP数据库内的地址细分为省市区
    ---------
    @params :num_config : 每次处理ip信息的记录数, 默认为20000.
             start_id : 处理ip信息的起始记录索引值, 默认为1.
             college_tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info".
             college_filename : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             correct_filename : 自定义纠错文件的json文件名或路径,默认为"../data/correct.json".
             sqlite3file : sqlite3数据库文件名或路径，默认为"../data/ipdata.db".
    -------
    @Returns  :None
    -------
    """
    if num_config is None:
        num_config = 20000 
    if start_id is None:
        start_id = 1
    if college_tablename is None:
        college_tablename = 'college_info'
    if college_filename is None:
        college_filename =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if correct_filename is None:
        correct_filename =  os.path.abspath(data_dir+os.path.sep+"correct.json")
        file_set(correct_filename)
    
    convert(sql_object,college_tablename,num_config,start_id,college_filename,correct_filename,sqlite3file=sqlite3file)

def sqldump(sql_file,table_college_info_sql_file,table_iprange_info_sql_file,table_ipv6_range_info_sql_file):
    print( "连接IP数据库, 并导出为sql文件: \n---------------处理中, 请稍候---------------")
    if default_sql_export:
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, sql_file))
        print( "IP数据库sql脚本导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s college_info > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_college_info_sql_file))
        print( "高校信息表sql脚本导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s iprange_info > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_iprange_info_sql_file))
        print( "IPv4数据表sql脚本导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s ipv6_range_info > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_ipv6_range_info_sql_file))
        print( "IPv6数据表sql脚本导出成功! \n")
    if default_gz_export:
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s | gzip > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, sql_file+'.gz'))
        print( "IP数据库gz压缩档导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s college_info | gzip > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_college_info_sql_file+'.gz'))
        print( "高校信息表gz压缩档导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s iprange_info | gzip > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_iprange_info_sql_file+'.gz'))
        print( "IPv4数据表gz压缩档导出成功! ")
        os.system('mysqldump --net-buffer-length=%s -h %s -P %s -u %s -p%s %s ipv6_range_info | gzip > %s' % (config['mysql'].net_buffer_length, config['mysql'].host, config['mysql'].port, config['mysql'].user, config['mysql'].password, config['mysql'].ip_database, table_ipv6_range_info_sql_file+'.gz'))
        print( "IPv6数据表gz压缩档导出成功! \n")
        
def sqlite3dump(sqlite3file):
    print( "将SQLite3数据库压缩为gz文件: \n---------------处理中, 请稍候---------------")
    if default_gz_export:
        os.system('gzip -kfq %s' % ( sqlite3file))
        print( "SQLite3数据库gz压缩档导出成功! \n")
    
if __name__ == '__main__':
    """
    @description  :实现纯真IP数据库和ZXinc_ipv6数据库的下载和更新.
    ---------
    @params  :None
    -------
    @Returns  :None
    -------
    """
    ipv4update,ipv6update = None,None

    filename =  os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
    txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
    ipv4update = dat2Txt(dat_filename=filename, txt_filename= txt_filename)

    v6filename =  DEFAULT_FILE_LOCATION
    v6txt_filename = os.path.abspath(data_dir+os.path.sep+"ipv6data.txt")
    if ipv4update:
        ipv6update = db2Txt(db_filename=v6filename, txt_filename= v6txt_filename, ipv4update=True)
    else:
        ipv6update = db2Txt(db_filename=v6filename, txt_filename= v6txt_filename)

    if default_sql_update:
        print( "===============MySQL数据库更新=============== \n")
        mysql = mysql_Database(config['mysql'].ip_database)
        if ipv4update:
            dat2Mysql(mysql)
            convertipv4(mysql)
        if ipv6update:
            db2Mysql(mysql,ipv6update=ipv6update)
        if ipv4update or ipv6update:
            sqldump(sql_file,table_college_info_sql_file,table_iprange_info_sql_file,table_ipv6_range_info_sql_file)

    if default_sqlite3_update:
        print( "===============SQLite3数据库更新=============== \n")
        sqlite3file = config['sqlite3'].ip_database
        sqlite3gz = sqlite3file+'.gz'
        if os.path.exists(sqlite3gz) and not os.path.exists(sqlite3file):
            os.system('gzip -dkf %s' % ( sqlite3gz))
        sqlite3 = sqlite3_Database(sqlite3file)
        if ipv4update:
            dat2SQLite3(sqlite3)
            convertipv4(sqlite3,sqlite3file=sqlite3file)
        if ipv6update:
            db2SQLite3(sqlite3)
        try:
            sqlite3.__del__()
        except:
            pass
        if ipv4update or ipv6update:
            sqlite3dump(sqlite3file)