# -*- encoding: utf-8 -*-
'''
@Description:  :ZXinc_IPv6数据库查询与更新
@Date          :2020/06/24 22:56:01
@Author        :Forked from https://github.com/lilydjwg/winterpy
@version       :2.0

Parse IPDB database files.
Get it here: http://ip.zxinc.org/

License: GPLv3 or later
'''

import os
import sys
import re
import time
import logging
import struct
import py7zr
import urllib.request
import __init__
from ipSearch import IPv6Loader
from ipUpdate import get_fetcher
from file_set import file_set
from typing import Union, Optional
try:
    from configs import default_txt_update
except :
    default_txt_update = False #当数据文件版本无更新时是否默认自动更新ipv6data.txt文件, False为默认不更新。

data_dir = __init__.data_dir
tmp_dir =__init__.tmp_dir
DEFAULT_FILE_LOCATION = __init__.DEFAULT_FILE_LOCATION
logger = logging.getLogger(__name__)

def db_down(filename, version_file):
    fetcher = get_fetcher()
    curr_version, check_time, update_time = (0, 0, 0)
    file_set(version_file,'file')
    with open(version_file, "rb+") as handle:
        content = handle.read()
        if len(content) > 0:
            curr_version, check_time, update_time = struct.unpack("<3I", content)
            print('本地IPv6数据文件版本: ' + str(curr_version))
            print('上次检查更新时间: ' + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(check_time))))
            print('上次数据更新时间: ' + str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(update_time))))
            print('')

    print('开始检查IPv6数据库更新: \n---------------处理中, 请稍候---------------')
    check_time = int(time.time())
    
    host = 'http://ip.zxinc.org'
    print('地址：' + host)
    try:
        D = IPv6Loader(filename)
    except OSError as e:
        print('注意：原IPv6数据文件无法打开：', e, file=sys.stderr)
        D = None

    if host.lower().startswith('http'):
        req = urllib.request.Request(
            host,
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
            })
    else:
        raise ValueError from None

    with urllib.request.urlopen(req, timeout=30) as res:
        page = res.read().decode('utf-8')
        m = re.search(r'href="([^"]+)".*?版本(\d{8})', page)
        date = int(m.group(2))
        remote_file = m.group(1)

        if D and date <= curr_version:
            noup = '当前IPv6数据文件版本 ('+ str(curr_version) + ')无更新!'
            print(noup)
            with open(version_file, "wb+") as handle:
                handle.write(struct.pack("<3I", date, check_time, update_time))
            return 0
        upstart = 'IPv6数据文件新版本: ' + str(date) 
        print(upstart)
        print( "------------------------------------------- \n " )
        print('开始更新IPv6数据文件: '+ filename + '\n---------------处理中, 请稍候---------------')
        update_time = int(time.time())
        tmp_path = os.path.join(tmp_dir, remote_file)
        data = fetcher(tmp_path,f'{host}/{remote_file}')
        if not data:
            print('下载出错，正在重试...')
            data = fetcher(tmp_path,f'{host}/{remote_file}')
            if not data:
                return -3
        try:
            with py7zr.SevenZipFile(tmp_path, 'r') as archive:
                archive.extract(targets=['ipv6wry.db'],path=tmp_dir)
        except:
            logger.error(f'解压缩{tmp_path}时出错!')
            return -5
        if filename is None:
            return data
        if type(filename) is str:
            # save to filename
            try:
                tmp_path = os.path.join(tmp_dir, 'ipv6wry.db')
                with open(tmp_path, 'rb') as f:
                    d = f.read()
                try:
                    safe_overwrite(filename, d, mode='wb')
                finally :
                    os.remove(tmp_path)
                old_c = D.count if D else 0
                D = IPv6Loader(filename)
                print('已经更新！IPv6数据条数 %d->%d.' % (old_c, D.count),
                                file=sys.stderr)
                with open(version_file, "wb+") as handle:
                    handle.write(struct.pack("<3I", date, check_time, update_time))
                return len(data)
            except:
                logger.error('保存到最终文件时出错!')
                return -6
        else:
            logger.error('保存到最终文件时出错!')
            return -6
    

def safe_overwrite(fname: str,
                   data: Union[bytes, str],
                   *,
                   method: str = 'write',
                   mode: str = 'w',
                   encoding: Optional[str] = None) -> None:
    # FIXME: directory has no read perm
    # FIXME: symlinks and hard links
    tmpname = fname + '.tmp'
    # if not using "with", write can fail without exception
    with open(tmpname, mode, encoding=encoding) as f:
        getattr(f, method)(data)
        # see also: https://thunk.org/tytso/blog/2009/03/15/dont-fear-the-fsync/
        f.flush()
        os.fsync(f.fileno())
    # if the above write failed (because disk is full etc), the old data should be kept
    try:
        if os.path.exists(fname):
            os.remove(fname)
    except : 
        os.remove(tmpname)
        return
    os.rename(tmpname, fname)

def db_down_info(filename, version_file,ipv4update=False):
    file_set(filename)
    file_set(version_file)
    ret = db_down(filename, version_file)
    if ret > 0:
        print('成功写入到%s, %s字节' %
              (filename, format(ret, ','))
            )
        print( "------------------------------------------- \n " )
        return 1
    if ret == 0:
        print( "-------------------------------------------" )
        if not ipv4update and not default_txt_update:
            print( "正在退出IP数据库更新任务, 请稍候... \n " )
            sys.exit(0)
        else:
            print()
            return 0
    else:
        print('写入失败, 错误代码: %d' % ret)
        print( "-------------------------------------------" )
        if not default_txt_update:
            print( "正在退出IP数据库更新任务, 请稍候... \n " )
            sys.exit(1)
        else:
            print()
            return -1

def main():
    import argparse
    parser = argparse.ArgumentParser(description='ZXinc_IPv6数据库查询与更新')
    parser.add_argument('IP', nargs='*', help='要查询的IP')
    parser.add_argument('-f', '--file', default=DEFAULT_FILE_LOCATION, help='数据库文件路径')
    parser.add_argument('-v6', '--version_file', default=os.path.abspath(data_dir+os.path.sep+"ipv6data_version.bin"), help='数据库版本文件路径')
    parser.add_argument('-A', '--all', action='store_true', default=False, help='显示所有记录')
    parser.add_argument('-u', '--update', action='store_true', default=False, help='更新数据库')
    parser.add_argument('-Q', '--more-quiet', action='store_true', default=False, help='更新数据库时总是不输出内容')

    args = parser.parse_args()

    if args.update:
        db_down_info(args.file,args.version_file)

    try:
        D = IPv6Loader(args.file)
    except Exception as e:
        print(e)
        db_down_info(args.file,args.version_file)
        D = IPv6Loader(args.file)

    ips = args.IP
    if not ips:
        if not args.all:
            print(D)
        else:
            for info in D.iter():
                loc = ' '.join(info.info).strip()
                print(f'{info.start} - {info.end} {loc}')
    elif len(ips) == 1:
        print(' '.join(D.lookup(ips[0]).info))
    else:
        for ip in ips:
            print(D.lookup(ip))


if __name__ == '__main__':
    main()
