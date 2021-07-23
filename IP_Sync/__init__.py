import os
data_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))+os.path.sep+"data")
tmp_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))+os.path.sep+"tmp")
DEFAULT_FILE_LOCATION = os.path.join(data_dir,'ipv6wry.db')

sql_file = os.path.abspath(data_dir+os.path.sep+"ipdatabase.sql")
table_college_info_sql_file = os.path.abspath(data_dir+os.path.sep+"college_info.sql")
table_iprange_info_sql_file = os.path.abspath(data_dir+os.path.sep+"iprange_info.sql")
table_ipv6_range_info_sql_file = os.path.abspath(data_dir+os.path.sep+"ipv6_range_info.sql")
__all__ = ['collegeUpdate', 'convert','dat2mysql','dat2sqlite3','dat2txt','file_set','ip_Sync','ipSearch','ipUpdate','ipv6Update']