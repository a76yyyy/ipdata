# -*- encoding: utf-8 -*-
'''
@Description:  :IP数据库的查询功能
@Date          :2021/06/24 16:01:00
@Author        :a76yyyy
@version       :2.0
'''
import os
import socket
import logging
import mmap
import ipaddress
from struct import pack, unpack
import collections
from typing import Tuple, List
import __init__

DEFAULT_FILE_LOCATION = __init__.DEFAULT_FILE_LOCATION
'''
IPv4数据Tools
'''
class IPLoader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.db_buffer = None
        self.open_db()
        (self.idx_start, self.idx_end, self.idx_count) = self._get_index()

    def open_db(self):
        if not self.db_buffer:
            self.db_buffer = open(self.file_name, 'rb')
        return self.db_buffer

    def _get_index(self):
        """
        读取数据库中IP索引起始和结束偏移值
        """
        self.db_buffer.seek(0)
        # 文件头 8个字节，4字节开始索引偏移值+4字节结尾索引偏移值
        index_str = self.db_buffer.read(8)
        start, end = unpack('II', index_str)
        count = (end - start) // 7 + 1
        return start, end, count

    def read_ip(self, offset):
        """
        读取ip值（4字节整数值）
        返回IP值
        """
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(4)
        return unpack('I', buf)[0]

    def get_offset(self, offset):
        if offset:
            self.db_buffer.seek(offset)

        buf = self.db_buffer.read(3)
        return unpack('I', buf + b'\0')[0]

    def get_string(self, offset):
        """
        读取原始字符串（以"\0"结束）
        返回元组：字符串
        """
        if offset == 0:
            return 'None'

        flag = self.get_mode(offset)

        if flag == 0:
            return 'None'

        if flag == 2:
            offset = self.get_offset(offset + 1)
            return self.get_string(offset)

        self.db_buffer.seek(offset)

        ip_string = b''
        while True:
            ch = self.db_buffer.read(1)
            if ch == b'\0':
                break
            ip_string += ch

        return ip_string

    def get_mode(self, offset):
        # 偏移指针位置
        self.db_buffer.seek(offset)
        c = self.db_buffer.read(1)
        if not c:
            return 0
        return ord(c)

    def get_mode_offset(self):
        buf = self.db_buffer.read(3)
        return get_offset(buf)
    
    def get_ip(self,offset):
        # 移动指针位置
        self.db_buffer.seek(offset)
        buf = self.db_buffer.read(4)
        ip = socket.inet_ntoa(pack('!I', unpack('I', buf)[0]))
        return ip

    def get_ip_record(self, offset):
        # 移动指针位置
        self.db_buffer.seek(offset)

        # 获取mode
        mode = ord(self.db_buffer.read(1))

        if mode == 1:
            mode_1_offset = self.get_mode_offset()
            mode_ip_location = self.get_string(mode_1_offset)
            mode_1 = self.get_mode(mode_1_offset)
            if mode_1 == 2:
                mode_ip_info = self.get_string(mode_1_offset + 4)
            else:
                mode_ip_info = self.get_string(mode_1_offset + len(mode_ip_location) + 1)

        elif mode == 2:

            mode_ip_location = self.get_string(self.get_mode_offset())
            mode_ip_info = self.get_string(offset + 4)

        else:
            mode_ip_location = self.get_string(offset)
            mode_ip_info = self.get_string(offset + len(mode_ip_location) + 1)
 
        return mode_ip_location, mode_ip_info

# 将整数的IP转换成IP号段，例如（18433024 ---> 1.25.68.0）
def convert_int_ip_to_string(ip_int):
    return socket.inet_ntoa(pack('I', socket.htonl(ip_int)))

# IP 转换为 整数
def convert_string_ip_to_int(str_ip):
    try:
        ip = unpack('I', socket.inet_aton(str_ip))[0]
    except Exception as e:
        # 如果IP不合法返回 None
        logging.info(e)
        return None
    # ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)
    else:
        return socket.ntohl(ip)

# 转换字符
def convert_str_to_utf8(gbk_str):
    try:
        return gbk_str.decode('gbk').encode('utf-8')
    except Exception as e:
        # 当字符串解码失败，并且最一个字节值为'\x96',则去掉它，再解析
        logging.info(e)
        if gbk_str[-1] == '\x96':
            try:
                return gbk_str[:-1].decode('gbk').encode('utf-8') + '?'
            except Exception as e:
                logging.info(e)

        return 'None'

# 获取offset 值
def get_offset(buffer_string):
        return unpack('I', buffer_string + b'\0')[0]


'''
IPv6数据Tools
'''
logger = logging.getLogger(__name__)
class DatabaseError(Exception): pass

class IpInfo(collections.namedtuple('IpInfo', 'start end info')):
    pass

class IPv6Loader:
    def __init__(self, dbfile, charset='utf-8'):
        if isinstance(dbfile, (str, bytes, os.PathLike)):
            dbfile = open(dbfile, 'rb')

        self.charset = charset
        try:
            self.f = f = mmap.mmap(dbfile.fileno(),0,access=mmap.MAP_SHARED)
        except:
            self.f = f = mmap.mmap(dbfile.fileno(),0,access=mmap.ACCESS_READ)
        finally:
            dbfile.close()
        
        magic = f[0:4]
        if magic != b'IPDB':
            raise DatabaseError('bad magic')

        self.index_base_offset = unpack('<Q', f[16:24])[0] #索引区基址

        iplen = f[7]
        if iplen == 4:
            self.ip_version = 4
            self._read_index = self._read_index_v4
            self._int_to_ip = self._int_to_ip_v4
            real_count = (len(f) - self.index_base_offset) // 7
        elif iplen == 8:
            self.ip_version = 6
            self._read_index = self._read_index_v6
            self._int_to_ip = self._int_to_ip_v6
            real_count = (len(f) - self.index_base_offset) // 11
        else:
            raise DatabaseError('unsupported ip length', iplen)

        count = unpack('<Q', f[8:16])[0]
        if real_count != count:
            logger.warning('real count != reported count! %s != %s',
                                         real_count, count)
        self.count = real_count
        self.address_segment_len = f[24] if f[4] != 1 else 2

    def lookup(self, ip):
        ip = ipaddress.ip_address(ip)
        if ip.version != self.ip_version:
            raise ValueError('wrong IP address version, supported is %s' %
                             self.ip_version)

        if ip.version == 6:
            needle = int(ip) >> 8 * 8
        else:
            needle = int(ip)
        return self._search_record(needle)

    def _search_record(self, needle: int) -> IpInfo:
        lo = 0
        hi = self.count - 1
        read_index = self._read_index

        if needle < read_index(lo)[0]:
            raise LookupError('IP not found')
        ip, offset = read_index(hi)
        if needle >= ip:
            info = self._read_rec(offset)
            return IpInfo(self._int_to_ip(ip), None, info)

        loip = 0
        if self.ip_version == 4:
            hiip = 0xffff_ffff
        else:
            hiip = 0xffff_ffff_ffff_ffff

        hit = self.index_base_offset
        while lo + 1 < hi:
            mi = (lo + hi) // 2
            ip, offset = read_index(mi)
            if ip <= needle:
                lo = mi
                loip = ip
                hit = offset
            else:
                hi = mi
                hiip = ip

        info = self._read_rec(hit)
        return IpInfo(self._int_to_ip(loip), self._int_to_ip(hiip), info)

    def iter(self):
        read_index = self._read_index
        read_rec = self._read_rec
        int_to_ip = self._int_to_ip
        count = self.count

        last_ip, offset = read_index(0)
        info = read_rec(offset)
        i = 1
        while i < count:
            ip, offset = read_index(i)
            yield IpInfo(int_to_ip(last_ip), ipaddress.IPv6Address((ip << 8 * 8) - 1), info)

            last_ip = ip
            info = read_rec(offset)
            i += 1

        if self.ip_version == 4:
            hiip = 0xffff_ffff
        else:
            hiip = 0xffff_ffff_ffff_ffff

        yield IpInfo(int_to_ip(last_ip), ipaddress.IPv6Address((hiip << 8 * 8) + hiip), info)

    @staticmethod
    def _int_to_ip_v4(i: int) -> ipaddress.IPv4Address:
        return ipaddress.IPv4Address(i)

    @staticmethod
    def _int_to_ip_v6(i: int) -> ipaddress.IPv6Address:
        return ipaddress.IPv6Address(i << 8 * 8)

    def _read_index_v4(self, i):
        pos = self.index_base_offset + i * 7
        data = self.f[pos:pos + 7] + b'\x00'
        ip, offset = unpack('<LL', data)
        return ip, offset

    def _read_index_v6(self, i):
        pos = self.index_base_offset + i * 11
        data = self.f[pos:pos + 11] + b'\x00'
        ip, offset = unpack('<QL', data)
        logger.debug('reading index %d at %x, and got IP %s', i, pos,
                                 self._int_to_ip(ip))
        return ip, offset

    def _read_rec(self, pos: int) -> List[str]:
        logger.debug('reading record at %x', pos)
        f = self.f
        result = []
        for _ in range(self.address_segment_len):
            typ = f[pos]
            if typ == 2:
                new_pos = _parse_offset(f[pos + 1:pos + 4])
                s, _ = self._read_cstring(new_pos)
                pos += 4
            else:
                s, pos = self._read_cstring(pos)
            result.append(s)
        return result

    def _read_cstring(self, start: int) -> Tuple[str, int]:
        logger.debug('reading C string at %x', start)
        if start == 0:
            return '(null)', start + 1

        end = self.f.find(b'\x00', start)
        if end < 0:
            raise Exception('fail to read C string')
        data = self.f[start:end]
        return data.decode(self.charset, errors='replace'), end + 1

    def __str__(self):
        return ('%s %d条数据' % (
            ''.join(self.version_info()),
            self.count,
        ))

    def version_date(self):
        d = ''.join(x for x in self.version_info()[-1] if x.isdigit())
        return int(d)

    def version_info(self):
        _, pos = self._read_index(self.count - 1)
        return self._read_rec(pos)

def _parse_offset(data: bytes) -> int:
    data = data + b'\x00'
    return unpack('<L', data)[0]

def main():
    import argparse
    parser = argparse.ArgumentParser(description='zxinc IP数据库查询')
    parser.add_argument('IP', nargs='*', help='要查询的IP')
    parser.add_argument('-f', '--file', default=DEFAULT_FILE_LOCATION, help='数据库文件路径')

    args = parser.parse_args()
    D = IPv6Loader(args.file)

    ips = args.IP
    if not ips:
        print(D)
        return 
    print(D.lookup(ips[0]))

if __name__ == '__main__':
    main()