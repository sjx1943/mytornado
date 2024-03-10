#mysql数据库连接的基本操作

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

conn_url = 'mysql+pymysql://sgg:Zpepc001@localhost:3306/xianyu_db?charset=utf8mb4'
engine = create_engine(conn_url, echo=True, pool_recycle=3600)
Base = declarative_base()
