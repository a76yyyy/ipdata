# -*- encoding: utf-8 -*-
'''
@Description:  :将纯真IP数据库的txt文件或ZXinc_IPv6数据库的db文件转换至sqlite3数据库指定表中
@Date          :2020/07/23 20:22:15
@Author        :a76yyyy
@version       :1.0
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from database import sqlite3_Database
from configs import config
import socket
import struct
import getopt
from socket import inet_pton,AF_INET6
from file_set import file_set
from __init__ import data_dir,tmp_dir,DEFAULT_FILE_LOCATION
from ipSearch import IPLoader,IPv6Loader
from ipUpdate import dat_down_info
from ipv6Update import db_down_info
from dat2txt import get_ip_info


def usage():
    print(
        '函数功能     : 将纯真IP数据库的txt文件或ZXinc_IPv6数据库的db文件转换至sqlite3数据库指定表中.\n' +
        '外部参数输入 : \n       ' +
        '-d : 输入sqlite3数据库db文件的文件名或路径,默认为"../data/ipdata.db",\n       '+
        '-h : 返回帮助信息,\n       '+
        '-t : sqlite3中IP数据库的表名,默认为"iprange_info",\n       '+
        '-f : 输入文本文件的文件名或路径,默认为"../data/czipdata.txt"\n       ' +
        '-t6 : sqlite3中IPv6数据库的ipv6信息表的表名,默认为"ipv6_range_info"\n       ' + 
        '-d6 : 输入ipv6数据库db文件的文件名或路径,默认为"../data/ipv6data.db"'
    )

def save_data_to_sqlite3(ip_line):
    try:
        begin = ip_line[0:16].replace(' ', '')
        end = ip_line[16:32].replace(' ', '')
        item = ip_line[32:].split(" ")
        try:
            location = item[0]
        except:
            location = ''
        try:
            isp_type= ' '.join(str(i) for i in item[1:]).split('\n')[0]
        except Exception as e:
            print(e)
            isp_type = ''

        this_line_value = ( begin, struct.unpack("!I",socket.inet_aton(begin))[0], end, struct.unpack("!I",socket.inet_aton(end))[0], location, isp_type)
        return this_line_value
    except Exception as e:
        print(e)

def dat2sqlite3(sqlite_object,ip_tablename,txt_filename):
    print('检索IPv4数据库是否存在 \n---------------处理中, 请稍候---------------')
    sqlite3 = sqlite_object
    code='DROP TABLE IF EXISTS `'+ ip_tablename +'`;'
    sqlite3.execute(code)
    code='''
    CREATE TABLE IF NOT EXISTS `'''+ ip_tablename +'''` (
        `id` INTEGER PRIMARY KEY NOT NULL, -- '主键'
        `ip_start` varchar(39) NOT NULL, -- '起始IP'
        `ip_start_num` varbinary(16) NOT NULL, -- 'IP起始整数'
        `ip_end` varchar(39) NOT NULL, -- '结束IP'
        `ip_end_num` varbinary(16) NOT NULL, -- 'IP结束整数'
        `country` varchar(200) NOT NULL DEFAULT '', -- '国家/地区/组织'
        `province` varchar(200) NOT NULL DEFAULT '', -- '省/自治区/直辖市'
        `city` varchar(200) NOT NULL DEFAULT '', -- '地级市'
        `area` varchar(200) NOT NULL DEFAULT '', -- '县/区/乡/镇/街道'
        `address` varchar(200) NOT NULL DEFAULT '', -- '详细地址'
        `location` varchar(200) NOT NULL DEFAULT '', -- '运营商/节点'
        `UpdateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- '更新日期'
        );
    '''
    sqlite3.execute(code)
    sqlite3.execute('CREATE INDEX `idx_start_end_number` ON `'+ ip_tablename +'` (`ip_start_num`,`ip_end_num`);')
    ip_file = open(txt_filename,encoding="utf-8")
    print('将IPv4数据文件"'+ txt_filename +'"导入sqlite3数据库中: \n---------------处理中, 请稍候---------------')
    ary = []
    i = 0
    j = 0
    insert_sql = 'INSERT  INTO `'+ ip_tablename +'` ( `ip_start`, `ip_start_num`, `ip_end`, `ip_end_num`, `address`, `location`) VALUES ( ?, ?, ?, ?, ?, ? )'
    for line in ip_file:
        z=line
        i = i+1
        ary.append(save_data_to_sqlite3(z))
        if '255.255.255.0' in z:
            break
        if len(ary)>=100000:
            sqlite3.insert(insert_sql, ary)
            print("本批次（行：" + str(j) + " - " + str(j+99999) + "）已处理完成。共需处理" + str(100000) + "条，成功转换" + str(i-j) + "条。")
            j = j +100000
            print("系统将自动处理下一批IPv4数据（行：" + str(j) + " - " + str(j+99999) + "）…… \n---------------处理中, 请稍候---------------")
            ary = []
    if ary and len(ary)>0:
        sqlite3.insert(insert_sql, ary)
        print( "本批次（行：" + str(j) + " - " + str( j + len(ary) -1) + "）已处理完成。共需处理" + str(len(ary)) + "条，成功转换" + str(i-j) + "条。" )
        print( "-------------------------------------------" )
        print('已全部导入完成, 共导入'+str(i)+'条IPv4数据.\n')
        ary = []
    ip_file.close()


def db2sqlite3(sqlite_object,ipv6_tablename,db_filename):
    print('检索IPv6数据库是否存在 \n---------------处理中, 请稍候---------------')
    sqlite3 = sqlite_object
    code='DROP TABLE IF EXISTS `'+ ipv6_tablename +'`;'
    sqlite3.execute(code)
    code='''
    CREATE TABLE IF NOT EXISTS `'''+ ipv6_tablename +'''` (
        `id` INTEGER PRIMARY KEY NOT NULL, -- '主键'
        `ip_start` varchar(39) NOT NULL, -- '起始IP'
        `ip_start_num` varbinary(16) NOT NULL, -- 'IP起始整数'
        `ip_end` varchar(39) NOT NULL, -- '结束IP'
        `ip_end_num` varbinary(16) NOT NULL, -- 'IP结束整数'
        `country` varchar(200) NOT NULL DEFAULT '', -- '国家/地区/组织'
        `province` varchar(200) NOT NULL DEFAULT '', -- '省/自治区/直辖市'
        `city` varchar(200) NOT NULL DEFAULT '', -- '地级市'
        `area` varchar(200) NOT NULL DEFAULT '', -- '县/区/乡/镇/街道'
        `address` varchar(200) NOT NULL DEFAULT '', -- '详细地址'
        `location` varchar(200) NOT NULL DEFAULT '', -- '运营商/节点'
        `UpdateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- '更新日期'
        );
    '''
    sqlite3.execute(code)
    sqlite3.execute('CREATE INDEX `idxv6_start_end_number` ON `'+ ipv6_tablename +'` (`ip_start_num`,`ip_end_num`);')
    D = IPv6Loader(db_filename)
    print('将IPv6数据文件"'+ db_filename +'"导入sqlite3数据库中: \n---------------处理中, 请稍候---------------')
    ary = []
    i = 0
    j = 0
    insert_sql = 'INSERT  INTO `'+ ipv6_tablename +'` ( `ip_start`, `ip_start_num`, `ip_end`, `ip_end_num`, `country`, `province`, `city`, `area`, `address`, `location`) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    for info in D.iter():
        if info.info[0]:
            tmpinfo = info.info[0].split('\t',3)
            if ' ' in tmpinfo[0] or '台湾' in tmpinfo[0] or '香港' in tmpinfo[0] or '澳门' in tmpinfo[0]:
                tmpinfo = tmpinfo[0].split(" ") + tmpinfo[1:]
            if len(tmpinfo) > 4:
                detinfo = tmpinfo[:3]
                detinfo.append(''.join(tmpinfo[3:]))
            else:
                detinfo = tmpinfo + ['']*(4-len(tmpinfo))
        else:
            detinfo = ['']*4
        address = ''.join(detinfo)
        if 'IANA保留地址' in address or 'IANA特殊地址' in address or '局域网' in address:
            detinfo = ['']*4
        i = i+1
        z=(str(info.start), inet_pton(AF_INET6,str(info.start)), str(info.end), inet_pton(AF_INET6,str(info.end)), detinfo[0], detinfo[1], detinfo[2], detinfo[3], address , info.info[1])
        ary.append(z)
        if len(ary)>=50000:
            sqlite3.insert(insert_sql, ary)
            print("本批次（行：" + str(j) + " - " + str(j+49999) + "）已处理完成。共需处理" + str(50000) + "条，成功转换" + str(i-j) + "条。")
            j = j +50000
            print("系统将自动处理下一批IPv6数据（行：" + str(j) + " - " + str(j+49999) + "）…… \n---------------处理中, 请稍候---------------")
            ary = []
    if ary and len(ary)>0:
        sqlite3.insert(insert_sql, ary)
        print( "本批次（行：" + str(j) + " - " + str( j + len(ary) -1) + "）已处理完成。共需处理" + str(len(ary)) + "条，成功转换" + str(i-j) + "条。" )
        print( "-------------------------------------------" )
        print('已全部导入完成, 共导入'+str(i)+'条IPv6数据.\n')
        ary = []

if __name__ == '__main__':
    """
    @description  :将纯真IP数据库的txt文件或ZXinc_IPv6数据库的db文件转换至sqlite3数据库指定表中
    ---------
    @params  :-d : 输入sqlite3数据库db文件的文件名或路径,默认为"../data/ipdata.db",
             -t : sqlite3中IP数据库的ip信息表的表名,默认为"iprange_info"
             -f : 输入ipv4数据库文本文件的文件名或路径,默认为"../data/czipdata.txt"
             -t6 : sqlite3中IPv6数据库的ipv6信息表的表名,默认为"ipv6_range_info"
             -d6 : 输入ipv6数据库db文件的文件名或路径,默认为"../data/ipv6data.db"
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-d:-t:-f:-t6:-d6:',['help','sqlite3file=','tablename=','txtfile=','v6tablename=','v6dbfile='])
    varlist = []
    main_table_info = 0
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt_name in ('-d','--sqlite3file'):
            ip_database = opt_value
            sqlite_object = sqlite3_Database(ip_database)
            varlist.append('sqlite3file')
        elif opt_name in ('-t','--tablename'):
            ip_tablename = opt_value
            varlist.append('ip_tablename')
            main_table_info = 1
        elif opt_name in ('-t','--txtfile'):
            txt_filename = opt_value
            varlist.append('txt_filename')
            main_table_info = 1
        elif opt_name in ('-t6','--v6tablename'):
            ipv6_tablename = opt_value
            varlist.append('ipv6_tablename')
            main_table_info = 2
        elif opt_name in ('-d','--v6dbfile'):
            db_filename = opt_value
            varlist.append('db_filename')
            main_table_info = 2
    file_set(tmp_dir,'dir')
    file_set(data_dir,'dir')
    if 'sqlite3file' not in varlist:
        sqlite_object = sqlite3_Database(config['sqlite3'].ip_database)
    if main_table_info in (0, 1):
        if 'ip_tablename' not in varlist:
            ip_tablename = 'iprange_info'
        if 'txt_filename' not in varlist:
            txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
            if not file_set(txt_filename):
                dat_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
                czip_version_file = os.path.abspath(data_dir+os.path.sep+"czipdata_version.bin")
                if not file_set(dat_filename):
                    dat_down_info(dat_filename,czip_version_file)
                q = IPLoader(dat_filename)
                get_ip_info(dat_filename,txt_filename,0,q.idx_count)
        dat2sqlite3(sqlite_object,ip_tablename,txt_filename)
    if main_table_info in (0, 2):
        if 'ipv6_tablename' not in varlist:
            ipv6_tablename = 'ipv6_range_info'
        if 'db_filename' not in varlist:
            db_filename = DEFAULT_FILE_LOCATION
            if not file_set(db_filename):
                version_file = os.path.abspath(data_dir+os.path.sep+"ipv6data_version.bin")
                db_down_info(db_filename,version_file)
        db2sqlite3(sqlite_object,ipv6_tablename,db_filename)