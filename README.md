<img align="right" src="https://github-readme-stats.vercel.app/api?username=a76yyyy&show_icons=true&icon_color=CE1D2D&text_color=718096&bg_color=ffffff&hide_title=true" />

# IPDATA

[![](https://img.shields.io/github/stars/a76yyyy/ipdata?style=social)](https://github.com/a76yyyy/ipdata/stargazers) 
[![](https://img.shields.io/github/watchers/a76yyyy/ipdata?style=social)](https://github.com/a76yyyy/ipdata/watchers)
[![](https://img.shields.io/github/forks/a76yyyy/ipdata?style=social)](https://github.com/a76yyyy/ipdata/network/members)

[![](https://img.shields.io/badge/HomePage-a76yyyy-brightgreen)](https://www.a76yyyy.cn) 
[![](https://img.shields.io/github/license/a76yyyy/ipdata)](https://github.com/a76yyyy/ipdata/blob/main/LICENSE) 
[![](https://img.shields.io/github/last-commit/a76yyyy/ipdata)](https://github.com/a76yyyy/ipdata/)
[![](https://img.shields.io/github/commit-activity/m/a76yyyy/ipdata)](https://github.com/a76yyyy/ipdata/)
![](https://img.shields.io/github/repo-size/a76yyyy/ipdata)
![](https://img.shields.io/github/pipenv/locked/python-version/a76yyyy/ipdata)
[![Update](https://github.com/a76yyyy/ipdata/actions/workflows/update.yml/badge.svg)](https://github.com/a76yyyy/ipdata/actions/workflows/update.yml)
[![Create Release](https://github.com/a76yyyy/ipdata/actions/workflows/create-release.yml/badge.svg)](https://github.com/a76yyyy/ipdata/actions/workflows/create-release.yml)


纯真IPv4数据库镜像 / ZXinc_IPv6数据库镜像 & MySQL脚本/SQLite3 同步更新 for Python3(原czipdata项目)
(数据文件已通过release发布)

Github：[https://github.com/a76yyyy/ipdata](https://github.com/a76yyyy/ipdata)(推荐)

Gitee ：[https://gitee.com/a76yyyy/ipdata](https://gitee.com/a76yyyy/ipdata)(更新频率较低)

<a href="https://info.flagcounter.com/Fsfs">
<img align="right" src="https://s05.flagcounter.com/count2/Fsfs/bg_FFFFFF/txt_000000/border_CCCCCC/columns_4/maxflags_12/viewers_0/labels_1/pageviews_1/flags_0/percent_0/" alt="Flag Counter" border="0"></a>

# 功能

1. 通过Python实现[纯真IPv4](https://update.cz88.net/)数据库及[ZXinc_ipv6](http://ip.zxinc.org/)数据库的镜像更新，数据库在data文件夹下;
2. 将数据文件解析为txt格式;
3. 将数据文件全量导入mysql中，请先安装mysql并启用服务;
4. 将数据文件全量导入SQLite3中，请先安装SQLite3并启用服务;
5. 将MySQL/SQLite3数据库中的IP数据库内的地址细分为省市区;
6. 生成sql脚本文件的gz压缩文档，请先安装 gzip 并添加至系统变量(默认提供gz压缩文档, 不提供sql脚本);
7. 生成SQLite3数据库db文件的gz压缩文档;
8. Windows使用BAT文件实现数据库的自动更新和推送;
9. 结合计划任务可实现windows的定时更新。

# 数据文件

文件 | 内容 | 类型
---|:---:|:---:
czipdata_version.bin|IPv4本地数据文件版本记录|Binary
ipv6data_version.bin|IPv6本地数据文件版本记录|Binary
ipdata.db|IP数据库db文件|SQLite3 DB文件
ipdatabase.sql|IP数据库sql脚本(含以下sql内容)|MySQL脚本
iprange_info.sql|纯真IPv4数据表sql脚本|MySQL脚本
ipv6_range_info.sql|ZXinc_IPv6数据表sql脚本|MySQL脚本
college_info.sql|高校信息表sql脚本|MySQL脚本
czipdata.dat|纯真IPv4数据文件|IPDB源文件
ipv6data.db|ZXinc_IPv6数据文件|IPDB源文件(Not SQLite3)
czipdata.txt|纯真IPv4数据文本文件|TXT
ipv6data.txt|ZXinc_IPv6数据文本文件|TXT
correct.json|地址细分纠错文件|JSON

# IP查询
## 安装相关模块
```powershell
# 使用git前请先安装git软件
git clone --depth=1 https://github.com/a76yyyy/ipdata.git
cd ipdata
# 安装gzip 解压data文件夹中的gz相关文件;
# 使用sqlite3请先安装sqlite3软件, 数据库文件在data/ipdata.db.gz压缩档内;
# 使用mysql请先安装mysql组件并导入sql脚本, sql脚本在data/ipdatabase.sql.gz压缩档内;
# 进行下述操作前请先安装python3;
pip3 install pipenv
pipenv install
pipenv shell
python
```
## SQLite3 for Python3
```python
from database import sqlite3_Database
from configs import config
sqlite3file = config['sqlite3'].ip_database
conn = sqlite3_Database(sqlite3file)
```
## MySQL for Python3
```python
from database import mysql_Database
from configs import config
conn = mysql_Database(config['mysql'].ip_database)
```
## IPv4 查询
```python
import ipaddress
ip = ipaddress.IPv4Address('114.114.114.114')
sql = "select * from iprange_info where " + str(int(ip)) +" between ip_start_num and ip_end_num " 
print(conn.query(sql))
```
## IPv6 查询
```python
import ipaddress
ip = ipaddress.IPv6Address('2400:3200::')
sql = "select * from ipv6_range_info where x'" + ''.join(ip.exploded.split(':')) +"' between ip_start_num and ip_end_num " 
print(conn.query(sql))
```
## 退出
```python
conn.__del__()
exit()
```

# TODO

1. 实现data文件夹的分类存储;
2. 实现数据库的增量更新;
3. 实现Linux定时更新.

# 图片

![image](pic/mysql.png)

![image](pic/ipv6_range.png)

![image](pic/sql.png)

![image](pic/txt.png)

# [API](https://api.a76yyyy.cn/ip)

![image](pic/ip.png)

示例IPv4 API接口(暂不提供源码):[https://api.a76yyyy.cn/ip?function=ipInfo&params1=114.114.114.114](https://api.a76yyyy.cn/ip?function=ipInfo&params1=114.114.114.114)

![image](pic/api.png)

示例IPv6 API接口(暂不提供源码):[https://api.a76yyyy.cn/ip?function=ipv6Info&params1=2400:3200::1](https://api.a76yyyy.cn/ip?function=ipv6Info&params1=2400:3200::1)

![image](pic/v6api.png)

## Stargazers over time

[![Stargazers over time](https://starchart.cc/a76yyyy/ipdata.svg)](https://starchart.cc/a76yyyy/ipdata)