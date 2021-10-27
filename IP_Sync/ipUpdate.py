# -*- encoding: utf-8 -*-
'''
@Description:  :从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名
@Date          :2020/06/24 13:08:52
@Author        :a76yyyy
@version       :2.0
'''
#
# 用于从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名
# for Python 3.0+
# forked from https://pypi.python.org/pypi/qqwry-py3
#
# 当参数filename是str类型时，表示要保存的文件名。
# 成功后返回一个正整数，是文件的字节数；失败则返回一个负整数。
#
# 当参数filename是None时，函数直接返回qqwry.dat的文件内容（一个bytes对象）。
# 成功后返回一个bytes对象；失败则返回一个负整数。这里要判断一下返回值的类型是bytes还是int。
#
# 负整数表示的错误：
# -1：下载copywrite.rar时出错
# -2：解析copywrite.rar时出错
# -3：下载qqwry.rar时出错
# -4：qqwry.rar文件大小不符合copywrite.rar的数据
# -5：解压缩qqwry.rar时出错
# -6：保存到最终文件时出错

import os
import sys
import struct
import urllib.request
import zlib
import logging
import getopt
import requests
import time
import __init__
from file_set import file_set
try:
    from configs import default_txt_update
except :
    default_txt_update = False #当数据文件版本无更新时是否默认自动更新czipdata.txt文件, False为默认不更新。

logger = logging.getLogger(__name__)
tmp_dir = __init__.tmp_dir
file_set(tmp_dir,'dir')
data_dir = __init__.data_dir
file_set(data_dir,'dir')

def usage():
    print(
        '函数功能     : 从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名.\n' +
        '外部参数输入 : \n       ' +
        '-h : 返回帮助信息,\n       '+
        '-f : 输出纯真IP数据库的dat文件名或路径,默认为"czipdata.dat".'
    )


class ProgressBar:
    def __init__(self, title,count=0.0,run_status=None,fin_status=None,total=100.0,unit='', sep='/',chunk_size=1.0):
        # super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status,
                             self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


def get_fetcher():
    def open_url(file_name, url):
        try:
            print('地址：' + url)
            print('开始下载:' + file_name)
            start_time = time.time()
            headers = {
                "User-Agent": "Mozilla/3.0 (compatible; Indy Library)",
                "Accept": "text/html, */*"
            }
            from contextlib import closing
            with closing(requests.get(url, headers=headers,
                                      stream=True)) as response:
                chunk_size = 1024  # 单次请求最大值
                content_size = int(
                    response.headers['content-length'])  # 内容体总大小
                if content_size == 0:
                    raise Exception('文件大小为零')
                progress = ProgressBar(file_name,
                                       total=content_size,
                                       unit="KB",
                                       chunk_size=chunk_size,
                                       run_status="正在下载",
                                       fin_status="下载完成")
                with open(file_name, "wb+") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))
                end_time = time.time()
            print('下载完成,共花费了{:.2f}s'.format(end_time - start_time))
            with open(file_name, "rb+") as file:
                dat = file.read()
                if not dat:
                    raise Exception('文件大小为零')
                return dat
        except Exception as e:
            print(e)
            logger.error('下载%s时出错: %s', file_name, str(e))
            return None

    return open_url


def dat_down(filename,version_file):
    fetcher = get_fetcher()

    curr_version, check_time, update_time = (0, 0, 0)
    file_set(version_file,'file')
    with open(version_file, "rb+") as handle:
        content = handle.read()
        if len(content) > 0:
            curr_version, check_time, update_time = struct.unpack("<3I", content)
            print('本地IPv4数据文件版本: ' + str(curr_version))
            print('上次检查更新时间: ' + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(check_time))))
            print('上次数据更新时间: ' + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(update_time))))
            print('')

    print('开始检查IPv4数据库更新: \n---------------处理中, 请稍候---------------')
    check_time = int(time.time())
    # download copywrite.rar
    x = 0
    url = 'http://update.cz88.net/ip/copywrite.rar'
    copywrite_file =  os.path.abspath(tmp_dir + os.path.sep + 'copywrite.rar')
    data = fetcher(copywrite_file, url)
    if not data:
        print('获取信息失败, 正在重试...')
        data = fetcher(copywrite_file, url)
        if not data:
            print('获取信息失败, 尝试从Github获取更新信息!')
            url = 'https://raw.githubusercontent.com/a76yyyy/ipdata/main/tmp/copywrite.rar'
            data = fetcher(copywrite_file, url)
            x = 1
            if not data:
                print('获取信息失败, 尝试从jsdelivr获取更新信息!')
                url = 'https://cdn.jsdelivr.net/gh/a76yyyy/ipdata@main/tmp/copywrite.rar'
                data = fetcher(copywrite_file, url)
                x = 2
                if not data:
                    print('获取信息失败, 尝试从Github镜像站获取更新信息!')
                    url = 'https://raw.fastgit.org/a76yyyy/ipdata/main/tmp/copywrite.rar'
                    data = fetcher(copywrite_file, url)
                    x = 3
                    if not data:
                        print('获取信息失败, 尝试从Gitee获取更新信息!')
                        url = 'https://gitee.com/a76yyyy/ipdata/raw/main/tmp/copywrite.rar'
                        data = fetcher(copywrite_file, url)
                        x = 4
                        if not data:
                            print('获取信息失败!')
                            return -1

    # extract infomation from copywrite.rar
    if len(data) <= 24 or data[:4] != b'CZIP':
        logger.error('解析copywrite.rar时出错')
        return -2
    version, unknown1, size, _ , key = \
        struct.unpack_from('<IIIII', data, 4)
    if unknown1 != 1:
        logger.error('解析copywrite.rar时出错')
        return -2
    if version == curr_version:
        noup = '当前IPv4数据文件版本 ('+ str(curr_version) + ')无更新!'
        logger.info(noup)
        print(noup)
        with open(version_file, "wb+") as handle:
            handle.write(struct.pack("<3I", version, check_time, update_time))
        return 0
    upstart = 'IPv4数据文件新版本: ' + str(version) + ', 大小: ' + str(size)
    logger.info(upstart)
    print(upstart)
    print( "------------------------------------------- \n " )
    print('开始更新IPv4数据文件: '+ filename + '\n---------------处理中, 请稍候---------------')
    # download qqwry.rar
    update_time = int(time.time())
    if x == 0:
        url = 'http://update.cz88.net/ip/qqwry.rar'
    elif x == 1:
        url = 'https://raw.githubusercontent.com/a76yyyy/ipdata/main/tmp/qqwry.rar'
    elif x == 2:
        url = 'https://cdn.jsdelivr.net/gh/a76yyyy/ipdata@main/tmp/qqwry.rar'
    elif x == 3:
        url = 'https://raw.fastgit.org/a76yyyy/ipdata/main/tmp/qqwry.rar'
    elif x == 4:
        url = 'https://gitee.com/a76yyyy/ipdata/raw/main/tmp/qqwry.rar'
    qqwry_file =  os.path.abspath(tmp_dir + os.path.sep + 'qqwry.rar')
    data = fetcher(qqwry_file, url)
    if not data:
        print('下载出错，正在重试...')
        data = fetcher(qqwry_file, url)
        if not data:
            return -3

    if size != len(data):
        logger.error('qqwry.rar文件大小不符合copywrite.rar的数据!')
        return -4

    # decrypt
    head = bytearray(0x200)
    for i in range(0x200):
        key = (key * 0x805 + 1) & 0xff
        head[i] = data[i] ^ key
    data = head + data[0x200:]

    # decompress
    try:
        data = zlib.decompress(data)
    except:
        logger.error('解压缩qqwry.rar时出错!')
        return -5

    if filename is None:
        return data
    if type(filename) is str:
        # save to file
        try:
            with open(filename, 'wb') as f:
                f.write(data)
            with open(version_file, "wb+") as handle:
                handle.write(struct.pack("<3I", version, check_time, update_time))
            return len(data)
        except:
            logger.error('保存到最终文件时出错!')
            return -6
    else:
        logger.error('保存到最终文件时出错!')
        return -6

def dat_down_info(filename,czip_version_file,v6_updated=False):
    file_set(filename)
    file_set(czip_version_file)
    ret = dat_down(filename,czip_version_file)
    if ret > 0:
        print('成功写入到%s, %s字节' %
              (filename, format(ret, ','))
            )
        print( "------------------------------------------- \n " )
        return 1
    if ret == 0:
        print( "-------------------------------------------" )
        if not default_txt_update and v6_updated:
            print( "正在退出IP数据库更新任务, 请稍候... \n " )
            sys.exit(0)
        else:
            print()
            return 0
    else:
        print('写入失败, 错误代码: %d' % ret)
        print( "-------------------------------------------" )
        if not default_txt_update and v6_updated:
            print( "正在退出IP数据库更新任务, 请稍候... \n " )
            sys.exit(1)
        else:
            print()
            return -1

if __name__ == '__main__':
    """
    @description  :从纯真网络(cz88.net)导入qqwry.dat至指定dat格式文件名.
    ---------
    @param  :filename : 输出纯真IP数据库的dat文件名或路径,默认为"czipdata.dat"
             version_file : 纯真IP数据库的版本文件名或路径,默认为"czipdata_version.bin".
    -------
    @Returns  :None
    -------
    """
    opts,args = getopt.getopt(sys.argv[1:],'-h-f:-v',['help','filename=','version_file='])
    varlist = []
    for opt_name,opt_value in opts:
        if opt_name in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt_name in ('-f','--filename'):
            filename = opt_value
            varlist.append('filename')
        elif opt_name in ('-v','--version_file'):
            czip_version_file = opt_value
            varlist.append('version_file')
    if 'filename' not in varlist:
        filename =  os.path.abspath(data_dir+os.path.sep+"czipdata.dat")
    if 'version_file' not in varlist:
        czip_version_file = os.path.abspath(data_dir+os.path.sep+"czipdata_version.bin")
    dat_down_info(filename,czip_version_file)