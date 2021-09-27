# -*- encoding: utf-8 -*-
'''
@Description:  :将纯真IP数据库内的地址细分为省市区.
@Date          :2020/10/08 20:04:08
@Author        :a76yyyy
@version       :1.0

'''

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from database import mysql_Database,sqlite3_Database
from configs import config
import re
import collegeUpdate
from fuzzywuzzy import process
import json
from file_set import file_set
import getopt
from __init__ import tmp_dir,data_dir

def usage():
    print(
        '函数功能     : 将纯真IP数据库内的地址细分为省市区.\n' +
        '外部参数输入 : \n       ' +
        '-d : 输入sqlite3数据库db文件的文件名或路径,默认为"../data/ipdata.db",\n       '+
        '-n : 每次处理ip信息的记录数, 默认为20000,\n       '+
        '-s : 处理ip信息的起始记录索引值, 默认为1,\n       '+
        '-t : mySQL中IP数据库的大学信息表的表名,默认为"college_info",\n       '+
        '-f : 输出大学数据的json文件名或路径,默认为"./tmp/college.json",\n       '+
        '-c : 自定义纠错文件的json文件名或路径,默认为"../data/correct.json".'
    )

def convert_ip(sql_object, college_tablename, num_config, start_id, correct_list, correct_json,sqlite3file=None) : #将IP数据库内的地址细分为省市区
    start_id = max(start_id, 1)
    next_id = start_id + num_config #下一次开始ID
    next_end_id = next_id + num_config #下一次结束ID

    sql = sql_object.query("select `id`,`address`,`location` from `iprange_info` limit " + str(start_id - 1) + "," + str(num_config))
    result_num = len(sql)
    i = 0
    addr_list = []
    for linelist in sql:
        #print(linelist)
        addr = linelist[ "address" ]
        addr = splitAddress( sql_object, college_tablename, addr, linelist[ "location" ], correct_list, correct_json)
        addr.append(start_id + i)
        addr_list.append(addr)
        i += 1
    #print(addr_list)
    if addr_list:
        if sqlite3file:
            sql_object.executemany( "update `iprange_info` set `country`= ? ,`province`= ? ,`city`= ? ,`area`= ?, `location`=?  where `id`= ? ",addr_list )
        else:
            sql_object.executemany( "update `iprange_info` set `country`= (%s) ,`province`= (%s) ,`city`= (%s) ,`area`= (%s), `location`=(%s)  where `id`= (%s) ",addr_list )
    else:
        print( "------------------------------------------- \n已全部完成转换。" )
        return

    if result_num == num_config:
        print( "本批次（行：" + str(start_id-1) + " - " + str( next_id - 2 ) + "）已处理完成。共需处理" + str(result_num) + "条，成功转换" + str(i) + "条。\n系统将自动处理下一批IP数据（行：" + str(next_id-1) + " - " + str(next_end_id-1) + "）…… \n---------------处理中, 请稍候---------------" )
        # try:
        #     sql_object.__del__()
        # finally:
        #     pass
        # if sqlite3file:
        #     sql_object = sqlite3_Database(sqlite3file)
        # else:
        #     sql_object = mysql_Database(config['mysql'].ip_database)
        convert_ip(sql_object, college_tablename, num_config, next_id, correct_list, correct_json,sqlite3file=sqlite3file)
    else:
        print( "本批次（行：" + str(start_id-1) + " - " + str( start_id + result_num -2 ) + "）已处理完成。共需处理" + str(result_num) + "条，成功转换" + str(i) + "条。" )
        print( "------------------------------------------- \n已全部完成转换。" )

def addslashes(s): #在指定的预定义字符前添加反斜杠
    # import pymysql
    if(isinstance(s,str)):
        d = {"\0": "", "&nbsp;" : " ", "\\":"\\\\", "\"": "\\\"", "\r":"\\r", "\n":"\\n"} 
        for x in d:
            s = s.replace(x, d.get(x))
        return "'"+s+"'"
       # return "'"+pymysql.escape_string(s)+"'"
    if s is None:
        return "NULL"
    return "'"+str(s)+"'"

def splitAddress( sql_object, college_tablename, address, location, correct_list, correct_json ): #从IP库的地址中提取省市区等数据
    country = ''
    province = ''
    city = ''
    area = ''
    index = None

    matches = re.match( '(.*?(亚太地区|加勒比海地区|北美地区|拉美地区|欧洲地区|欧美地区|美洲地区|非洲地区))', address )
    if matches:
        country = matches.group()
        address = address.replace( country, '' )
        index = 1

    matches = re.match('(.*?(中国))', address)
    if matches:
        country = '中国'
        index = 1


    matches = re.match( '(.*?(省|市|西藏|内蒙古|新疆|广西|宁夏|香港|澳门))', address )
    if matches:
        country = '中国'
        province = matches.group()
        address = address.replace( province, '' )
        index = 2
    
    matches = re.match( '(.*?(市|自治州|地区|区划|县))', address )
    if matches:
        city = matches.group()
        address = address.replace( city, '' )
        index = 3
    
    matches = re.match( '(.*?(市|区|县|镇|乡|街道))', address )
    if matches:
        area = matches.group()
        #address = address.replace( area, '' )
        index = 4
    
    matches = re.match( '(.*?(大学|学院|校区|宿舍))', address )
    if matches:
        country = '中国'
        college_name = matches.group()
        size,college_list,college_dict = college(sql_object, college_tablename, college_name)
        if size:
            matches1 = re.match('(.*(大学|学院|校区|南区))', address+location)
            college_name1 = matches1.group()
            res0 = process.extractOne(college_name, college_list)
            res1 = process.extractOne(college_name1, college_list)
            if res0[1] < res1[1]:
                if res0[1] >85 or res1[1]>85:
                    college_info = college_dict[college_list.index( res1[0] )]
                    province = college_info['province']
                    city = college_info['city']
                    area = college_info['area']
                    #print(res0[1],res1[1],college_info['name'],address,location)
                    #location = college_info['name'] + location
                elif res1[1]<65:
                    college_info = college_dict[college_list.index( res1[0] )]
                    #print(res0[1],res1[1],college_info['name'],address,location)
                else:
                    provincelist = []
                    citylist = []
                    arealist = []
                    for line in college_dict:
                        if line['province'] in provincelist:
                            pass
                        else:
                            provincelist.append(line['province'])
                        if line['city'] in citylist:
                            pass
                        else:
                            citylist.append(line['city'])
                        if line['area'] in arealist:
                            pass
                        else:
                            arealist.append(line['area'])
                    if len(provincelist) == 1:
                        province = provincelist[0]
                        if len(citylist) == 1:
                            city = citylist[0]
                            if len(arealist) == 1:
                                area = arealist[0]
                    #print(res0[1],res1[1],province,city,area,address,location)
            else:
                if res1[1] >85:
                    college_info = college_dict[college_list.index( res1[0] )]
                    province = college_info['province']
                    city = college_info['city']
                    area = college_info['area']
                    #if res1[1] != 100:
                    #    print(res0[1],res1[1],college_info['name'],address,location)
                    #location = college_info['name'] + location
                else:
                    provincelist = []
                    citylist = []
                    arealist = []
                    for line in college_dict:
                        if line['province'] in provincelist:
                            pass
                        else:
                            provincelist.append(line['province'])
                        if line['city'] in citylist:
                            pass
                        else:
                            citylist.append(line['city'])
                        if line['area'] in arealist:
                            pass
                        else:
                            arealist.append(line['area'])
                    if len(provincelist) == 1:
                        province = provincelist[0]
                        if len(citylist) == 1:
                            city = citylist[0]
                            if len(arealist) == 1:
                                area = arealist[0]
                    #print(res0[1],res1[1],province,city,area,address,location)
            #exit()
        index = 5
    
    correctname = address+location
    if correctname in correct_list:
        i = correct_list.index( correctname )
        country = correct_json[i]["country"]
        province = correct_json[i]["province"]
        city = correct_json[i]["city"]
        area = correct_json[i]["area"]
        index = -1

    if index is None:
        country = address

    return  [ country, province, city, area, location] 

def college(sql_object, college_tablename, college_name):
    college_name = '%%'+college_name + '%%'
    sql = sql_object.query("select * from `"+ college_tablename + "` where `name` like '" + college_name+"'")
    name = []
    if sql:
        for line in sql:
            name.append(line['name'])
        return len(sql),name,sql
    return 0,name,sql

def convert(sql_object,college_tablename,num_config,start_id,college_filename,correct_filename,sqlite3file = None):
    print( "连接IP数据库, 并检索大学数据库信息: \n---------------处理中, 请稍候---------------")
    conn = sql_object
    if sqlite3file:
        collegeExist = conn.query("SELECT * FROM sqlite_master where type='table' and name='"+ college_tablename + "'")
        if not collegeExist :
            print( "大学数据库不存在，重新部署中: \n---------------处理中, 请稍候---------------")
            collegeUpdate.collegeUpdate(college_filename, college_tablename,sqlite3file=sqlite3file)
    else:
        collegeExist = conn.query("SELECT * FROM information_schema.TABLES WHERE TABLE_NAME = '"+ college_tablename + "'")
        table_scheme = [collegeExist[i]['TABLE_SCHEMA'] for i in range(len(collegeExist))]
        if not collegeExist or config["mysql"].ip_database not in table_scheme:
            print( "大学数据库不存在，重新部署中: \n---------------处理中, 请稍候---------------")
            collegeUpdate.collegeUpdate(college_filename, college_tablename)
    print( "IP数据库连接成功! ")
    print('------------------------------------------- ')
    print( "开始载入纠错文件correct.json: \n---------------处理中, 请稍候---------------")
    file_set(correct_filename,'file')
    correct_file = open(correct_filename, 'r', encoding='utf-8')
    correct_str = correct_file.read()
    try:
        correct_json = json.loads(correct_str)
    except:
        correct_json = {}
    correct_list = []
    if correct_json:
        for line in correct_json:
            if line:
                correct_list.append(line["address"]+line["location"])
    #print(correct_list,correct_json)
    print( "载入完成! ")
    print('------------------------------------------- ')
    print( "将IP数据库内的地址细分为省市区: \n---------------处理中, 请稍候---------------")
    if sqlite3file:
        convert_ip(conn, college_tablename, num_config, start_id, correct_list, correct_json,sqlite3file)
    else:
        convert_ip(conn, college_tablename, num_config, start_id, correct_list, correct_json)
    correct_file.close()
    print( "操作完成! \n ")

if __name__ == '__main__':
    """
    @description :将纯真IP数据库内的地址细分为省市区
    ---------
    @params :sqlite3file : 输入sqlite3数据库db文件的文件名或路径,默认为"../data/ipdata.db",
             num_config : 每次处理ip信息的记录数, 默认为20000.
             start_id : 处理ip信息的起始记录索引值, 默认为1.
             college_tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info".
             college_filename : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             correct_filename : 自定义纠错文件的json文件名或路径,默认为"../data/correct.json".
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-d:-n:-s:-t:-f:-c:',['help','sqlite3file=','num_config','start_id','college_tablename=','college_filename=','correct_filename='])
    sqlite3_object,varlist = None,[]
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt_name in ('-d','--sqlite3file'):
            ip_database = opt_value
            varlist.append('sqlite3file')
        elif opt_name in ("-n", "--num_config"):
            num_config = int(opt_value)
            varlist.append('num_config')
        elif opt_name in ("-s", "--start_id"):
            start_id = int(opt_value)
            varlist.append('start_id')
        elif opt_name in ("-t", "--college_tablename"):
            college_tablename = opt_value
            varlist.append('college_tablename')
        elif opt_name in ('-f','--college_filename'):
            college_filename = opt_value
            varlist.append('college_filename')
        elif opt_name in ('-c','--correct_filename'):
            correct_filename = opt_value
            varlist.append('correct_filename')
    if 'num_config' not in varlist:
        num_config = 20000 
    if 'start_id' not in varlist:
        start_id = 1
    if 'college_tablename' not in varlist:
        college_tablename = 'college_info'
    if 'college_filename' not in varlist:
        file_set(tmp_dir,'dir')
        college_filename =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if 'correct_filename' not in varlist:
        file_set(data_dir,'dir')
        correct_filename =  os.path.abspath(data_dir+os.path.sep+"correct.json")
        file_set(correct_filename)
    sqlite3 = False
    if 'sqlite3file' not in varlist:
        sql_object = mysql_Database(config['mysql'].ip_database)
        convert(sql_object,college_tablename,num_config,start_id,college_filename,correct_filename)
    else:
        sql_object = sqlite3_Database(ip_database)
        convert(sql_object,college_tablename,num_config,start_id,college_filename,correct_filename,sqlite3file=ip_database)