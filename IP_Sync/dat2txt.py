# -*- encoding: utf-8 -*-
'''
@Description:  :将IP数据库的dat文件(IPv4 from 纯真ip)或db文件(IPv6 from ZXinc)转换为txt文本文件
@Date          :2020/06/24 23:09:46
@Author        :a76yyyy
@version       :2.0
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import getopt
import ipUpdate
import ipv6Update
from file_set import file_set
from ipSearch import IPLoader,convert_int_ip_to_string,convert_string_ip_to_int
from ipSearch import IPv6Loader
from __init__ import tmp_dir,data_dir
from __init__ import DEFAULT_FILE_LOCATION as ipv6_dbfile

def usage():
    print(
        '函数功能     : 将IP数据库的dat文件(IPv4 from 纯真ip)或db文件(IPv6 from ZXinc)转换为txt文本文件.\n' +
        '外部参数输入 : \n       ' +
        '-h : 返回帮助信息,\n       '+
        '-d : 纯真IP数据库的dat文件名或路径,默认为"czipdata.dat",\n       '+
        '-v : 纯真IP数据库的版本文件名或路径,默认为"czipdata_version.bin",\n       '+
        '-d6 : IPv6数据库的db文件名或路径，默认为"ipv6data.db",\n       '+
        '-v6 : IPv6数据库的版本文件名或路径,默认为"ipv6data_version.bin",\n       '+
        '-t : 输出文本文件的文件名或路径,默认为"czipdata.txt",\n       '+
        '-s : 起始索引, 默认为0,\n       '+
        '-e : 结束索引, 默认为IP数据库总记录数.'
    )


# 获取IP信息并写入文本文件中
def get_ip_info(dat_filename,txt_filename,left,right):
    D = IPLoader(dat_filename)
    ip_file = open(txt_filename,"w",encoding='utf-8')
    print('将IPv4数据文件写入文本文件中 dat -> txt')
    print( "-------------------------------------------" )
    print('写入文件 ' + txt_filename +' 中, 请稍候...')
    if D.idx_count - left >= right - left and right - left >= 0:
        for i in range(left,right):
            ip_offset = i
            idx_offset = D.idx_start + ip_offset * 7
            ip_start = D.get_ip(idx_offset)
            if idx_offset != D.idx_end:
                idx2_offset = idx_offset + 7
                nextIp = D.get_ip(idx2_offset)
                nextIp = convert_string_ip_to_int(nextIp)
                ip_end = convert_int_ip_to_string(nextIp-1)
            else:
                ip_end = '255.255.255.255'
            address_offset = D.get_offset(idx_offset + 4)
            (location, info) = D.get_ip_record(address_offset + 4)
            ip_location = location.decode('gbk')
            ip_info = info.decode('gbk')
            data = [ip_start.ljust(16),ip_end.ljust(16),ip_location,' ',ip_info,'\n']
            ip_file.writelines(data)
        ip_file.writelines('\n')
        ip_file.writelines('\n')
        ip_file.writelines("IP数据库共有数据 ： " + str(right-left) + " 条\n")
        print('写入完成, 写入 ' + str(right-left) +' 条数据.')
        print( "------------------------------------------- \n " )
    else:
        print('写入失败, IPv4数据库共' + str(D.idx_count) + '组数据, 请检查输入参数!')
    ip_file.close()

# 获取IP信息并写入文本文件中
def get_ipv6_info(db_filename,txt_filename,left,right):
    D = IPv6Loader(db_filename)
    ip_file = open(txt_filename, "w",encoding='utf-8')
    print('将IPv6数据文件写入文本文件中 db -> txt')
    print( "-------------------------------------------" )
    print('写入文件 ' + txt_filename + ' 中, 请稍候...')
    if D.count - left >= right - left and right - left >= 0:
        i = 0
        for info in D.iter():
            if i < left: continue
            if i > right: break
            #loc = ' '.join(info.info).strip()
            data = [str(info.start).ljust(40), str(info.end).ljust(40), str(info.info), '\n']
            ip_file.writelines(data)
        ip_file.writelines('\n')
        ip_file.writelines('\n')
        ip_file.writelines("IPv6数据库共有数据 ： " + str(right - left) + " 条\n")
        print('写入完成, 写入 ' + str(right-left) + ' 条数据.')
        print( "------------------------------------------- \n " )
    else:
        print('写入失败, IPv6数据库共' + str(D.count) + '组数据, 请检查输入参数!')
    ip_file.close()


if __name__ == '__main__':
    """
    @description  :将IP数据库的dat文件(IPv4 from 纯真ip)或db文件(IPv6 from ZXinc)转换为txt文本文件
    ---------
    @params  :-d : 纯真IP数据库的dat文件名或路径,默认为"czipdata.dat"
             -v : 纯真IP数据库的版本文件名或路径,默认为"czipdata_version.bin"
             -d6 : IPv6数据库的db文件名或路径，默认为"ipv6data.db"
             -v6 : IPv6数据库的版本文件名或路径,默认为"ipv6data_version.bin"
             -t : 输出文本文件的文件名或路径,默认为"czipdata.txt"
             -s : 起始索引, 默认为0
             -e : 结束索引, 默认为IP数据库总记录数.
    -------
    @Returns  :None
    -------
    """
    opts, args = getopt.getopt(sys.argv[1:], '-h-d:-v:-d6:-v6:-t:-s:-e:', [
        'help', 'datfile=', 'czip_version_file=', 'dbfile=', 'ipv6_version_file=','txtfile=','start=', 'end='])
    varlist = []
    main_dat_info = 0
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt_name in ('-d','--datfile'):
            dat_filename = opt_value
            D = IPLoader(dat_filename)
            varlist.append('dat_filename')
            main_dat_info = 1
        elif opt_name in ('-v','--czip_version_file'):
            czip_version_file = opt_value
            varlist.append('czip_version_file')
        elif opt_name in ('-d6','--dbfile'):
            db_filename = opt_value
            D6 = IPv6Loader(db_filename)
            varlist.append('db_filename')
            main_dat_info = 2
        elif opt_name in ('-v6','--ipv6_version_file'):
            ipv6_version_file = opt_value
            varlist.append('ipv6_version_file')
        elif opt_name in ('-t','--txtfile'):
            txt_filename = opt_value
            varlist.append('txt_filename')
        elif opt_name in ('-s','--start'):
            startIndex = int(opt_value)
            varlist.append('startIndex')
        elif opt_name in ('-e','--end'):
            endv6Index = endIndex = int(opt_value)
            varlist.append('endIndex')

    file_set(tmp_dir,'dir')
    file_set(data_dir,'dir')
    if 'startIndex' not in varlist:
        startIndex = 0
    if main_dat_info in (0, 1):
        if 'dat_filename' not in varlist:
            dat_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
        if 'czip_version_file' not in varlist:
            czip_version_file = os.path.abspath(data_dir+os.path.sep+"czipdata_version.bin")
            file_set(czip_version_file)
        if not file_set(dat_filename):
            ipUpdate.dat_down_info(dat_filename,czip_version_file)
        q = IPLoader(dat_filename)
        if 'txt_filename' not in varlist:
            txt_filename = os.path.abspath(data_dir+os.path.sep+"czipdata.txt")
            file_set(txt_filename)
        if 'endIndex' not in varlist:
            endIndex = q.idx_count
        get_ip_info(dat_filename,txt_filename,startIndex,endIndex)
    if main_dat_info in (0, 2):
        if 'db_filename' not in varlist:
            db_filename = os.path.abspath(data_dir+os.path.sep+"ipv6data.db")
        if 'ipv6_version_file' not in varlist:
            ipv6_version_file = os.path.abspath(data_dir+os.path.sep+"ipv6data_version.bin")
            file_set(ipv6_version_file)
        if not file_set(db_filename):
            ipv6Update.db_down_info(db_filename,ipv6_version_file)
        D = IPv6Loader(db_filename)
        if 'txt_filename' not in varlist:
            txtv6_filename = os.path.abspath(data_dir+os.path.sep+"ipv6data.txt")
            file_set(txtv6_filename)
        if 'endIndex' not in varlist:
            endv6Index = D.count
        get_ipv6_info(db_filename, txtv6_filename, startIndex,endv6Index)