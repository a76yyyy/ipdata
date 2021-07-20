# -*- encoding: utf-8 -*-
'''
@Description:  :从''https://github.com/pg7go/The-Location-Data-of-Schools-in-China''导入''大学-8084.json''至指定json格式文件名
@Date          :2020/10/28 12:30:41
@Author        :a76yyyy
@version       :1.0
'''

import sys,os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import requests
import json
import logging
from database import mysql_Database
from configs import config
import getopt
import time
from file_set import file_set
from __init__ import tmp_dir
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = logging.getLogger(__name__)

def usage():
    print(
        '函数功能     : 从''https://github.com/pg7go/The-Location-Data-of-Schools-in-China''导入''大学-8084.json''至指定json格式文件名.\n' +
        '外部参数输入 : \n       ' +
        '-h : 返回帮助信息,\n       '+
        '-f : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".,\n       '+
        '-t : mySQL中IP数据库的大学信息表的表名,默认为"college_info".'
    )

def jsonDownload(filename):
    def get_fetcher():
        # no proxy
        #proxy = urllib.request.ProxyHandler({})
        # opener
        #opener = urllib.request.build_opener(proxy)
        
        def open_url(file_name, url):
            # request对象
            #req = urllib.request.Request(url)
            try:
                req = requests.get(url,headers={'Connection':'close'})
                # r是HTTPResponse对象
                #r = opener.open(req, timeout=900)
                #dat = r.read()
                dat = req.content
                if not dat:
                    raise Exception('文件大小为零')
                return dat
            except Exception as e:
                logger.error('下载%s时出错: %s' % (file_name, str(e)))
                return None

        return open_url

    fetcher = get_fetcher()

    # download json
    print('从''https://github.com/pg7go/The-Location-Data-of-Schools-in-China''导入''大学-8084.json''至'+ filename )
    url = 'https://raw.githubusercontent.com/pg7go/The-Location-Data-of-Schools-in-China/master/%E5%A4%A7%E5%AD%A6-8084.json'
    data = fetcher('college.json', url)
    if not data:
        print('等待3s后重试...')
        time.sleep(3)
        data = fetcher('college.json', url)
        if not data:
            return -1

    if filename == None:
        return data
    elif type(filename) == str:
        # save to file
        try:
            with open(filename, 'wb') as f:
                f.write(data)
            return len(data)
        except:
            logger.error('保存到最终文件时出错')
            return -6
    else:
        logger.error('保存到最终文件时出错')
        return -6

def do_insert(mysql_object, row_data):
    try:
        insert_sql = """INSERT  INTO `college_info` (`name`, `province`, `city`, `area`, `lat`, `lng`, `address`, `location`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"""
        mysql_object.insert(insert_sql, row_data)
    except Exception as e:
        print(row_data)
        print(e)

def execute(mysql_object, row_data):
    try:
        mysql_object.execute(row_data)
    except Exception as e:
        print(row_data)
        print(e)

def load_json(filename):
    college_file = open(filename, 'r', encoding='utf-8')
    college_str = college_file.read()
    college_json = json.loads(college_str)
    college_file.close()
    return college_json

def convert_college(mysql_object, filename, college_tablename) :
    mysql = mysql_object
    code='''DROP TABLE IF EXISTS `'''+college_tablename+'''`;'''
    mysql.execute(code)

    code='''
    CREATE TABLE IF NOT EXISTS `'''+college_tablename+'''` (
        `id` int AUTO_INCREMENT NOT NULL,
        `name` varchar(200) NOT NULL,
        `province` varchar(200) NOT NULL,
        `city` varchar(200) NOT NULL,
        `area` varchar(200) NOT NULL,
        `lat` varchar(32) NOT NULL,
        `lng` varchar(32) NOT NULL,
        `address` varchar(200) NOT NULL,
        `location` varchar(100) NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;
    '''
    mysql.execute(code)
    print('将大学数据文件"'+ filename +'"导入Mysql数据库中: \n---------------处理中, 请稍候---------------')
    college_json = load_json(filename)
    insert_sql = 'INSERT  INTO `'+college_tablename+'` (`name`, `province`, `city`, `area`, `lat`, `lng`, `address`, `location`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)'
    ary = []
    i = 0
    j = 0
    for line in college_json:
        ary.append([line['name'], line['province'], line['city'], line['area'], line['location']['lat'], line['location']['lng'], line['address'], line['address'] + line['name']])
        i = i+1
        if len(ary)>=1000:
            mysql.insert(insert_sql,ary)
            print( "本批次（行：" + str(j) + " - " + str( j + len(ary) -1) + "）已处理完成。共需处理" + str(len(ary)) + "条，成功转换" + str(i-j) + "条。" )
            j = j +1000
            print("系统将自动处理下一批IP数据（行：" + str(j) + " - " + str(j+999) + "）…… \n---------------处理中, 请稍候---------------")
            ary = []
    if ary and len(ary)>0:
        mysql.insert(insert_sql,ary)
        print( "本批次（行：" + str(j) + " - " + str( j + len(ary) -1) + "）已处理完成。共需处理" + str(len(ary)) + "条，成功转换" + str(i-j) + "条。" )
        print( "------------------------------------------- " )
        print('已全部导入完成, 共导入'+str(i)+'条数据.\n')
        ary = []

def collegeUpdate(filename, college_tablename):
    ret = jsonDownload(filename)
    if ret > 0:
        print('成功将大学地址数据写入到%s, %s字节' %
              (filename, format(ret, ','))
            )
        print('------------------------------------------- ')
    else:
        print('写入失败, 错误代码: %d' % ret)
        print('------------------------------------------- ')
        print('尝试导入本地json文件...\n---------------处理中, 请稍候---------------')
        college_json = load_json(filename)
        if college_json:
            print('导入成功！')
            print('------------------------------------------- ')
        else:
            print('导入失败,请手动下载文件至'+filename)
            exit()
    mysql = mysql_Database(config['mysql'].ip_database)
    convert_college(mysql, filename, college_tablename)
    
if __name__ == '__main__':
    """
    @description  :从'https://github.com/pg7go/The-Location-Data-of-Schools-in-China'导入'大学-8084.json'至指定json格式文件名.
    ---------
    @param  :filename : 输出大学数据的json文件名或路径,默认为"./tmp/college.json".
             tablename : mySQL中IP数据库的大学信息表的表名,默认为"college_info".
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-t:-f:',['help','tablename=','filename='])
    varlist = []
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        if opt_name in ("-t", "--tablename"):
            college_tablename = opt_value
            varlist.append('tablename')
        if opt_name in ('-f','--filename'):
            filename = opt_value
            varlist.append('filename')
    if 'filename' not in varlist:
        file_set(tmp_dir)
        filename =  os.path.abspath(tmp_dir+os.path.sep+"college.json")
    if 'tablename' not in varlist:
        college_tablename = 'college_info'
    collegeUpdate(filename, college_tablename)