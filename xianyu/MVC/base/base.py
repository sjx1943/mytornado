#mysql数据库连接的基本操作
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import configparser
import os

# 读取配置文件
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

# 获取 MySQL 连接信息
mysql_user = config.get('mysql', 'user')
mysql_password = config.get('mysql', 'password')
mysql_host = config.get('mysql', 'host')
mysql_port = config.getint('mysql', 'port')
mysql_database = config.get('mysql', 'database')
mysql_charset = config.get('mysql', 'charset')

conn_url = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}?charset={mysql_charset}'
engine = create_engine(conn_url, echo=True, pool_recycle=3600)
Base = declarative_base()