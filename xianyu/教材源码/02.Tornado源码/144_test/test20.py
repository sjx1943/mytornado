#coding=utf-8

from sqlalchemy.engine import create_engine

#1.配置引擎
conn_url = 'mysql://root:123456@127.0.0.1:3306/db01?charset=utf8'
engine = create_engine(conn_url,encoding='utf-8',echo=True)

#声明ORM基类
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(bind=engine)

#引入字段类型
from sqlalchemy import Column
from sqlalchemy.types import Integer,String,Date,DateTime,Float,Text


#自定义模型类
class User(Base):
    __tablename__='t_user'

    userid = Column(Integer,primary_key=True,autoincrement=True)
    uname = Column(String(length=30),unique=True)
    pwd = Column(String(length=30))
    createtime = Column(Date)


from sqlalchemy.orm import sessionmaker
import datetime


def insertUser(uname,pwd):
    #创建连接池对象
    connpool = sessionmaker()

    #获取一个连接对象
    conn = connpool()

    #插入一条记录
    user = User(uname=uname,pwd=pwd,createtime=datetime.date.today())
    conn.add(user)

    #事务提交
    conn.commit()

    conn.refresh(user)


    #断开连接
    conn.close()

insertUser('zhangsan','123123')







