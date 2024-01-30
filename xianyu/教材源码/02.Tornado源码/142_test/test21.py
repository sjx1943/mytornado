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

    def __repr__(self):
        return u'<User:%s>'%self.uname


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

# insertUser('zhangsan','123123')


def insertUsers(users=[]):
    #创建连接池对象
    connpool = sessionmaker()

    #获取一个连接对象
    conn = connpool()

    #插入一条记录

    conn.add_all(users)

    #事务提交
    conn.commit()

    [conn.refresh(u) for u in users]


    #断开连接
    conn.close()




# insertUsers([User(uname='wangwu',pwd='123123',createtime=datetime.date.today()),User(uname='zhaoliu',pwd='234234',createtime=datetime.date.today())])


def queryAll():
    #创建连接池对象
    connpool = sessionmaker()

    #获取连接
    conn = connpool()

    #执行查询操作
    users = conn.query(User).all()

    #断开连接
    conn.close()

    return users

# print queryAll()



def queryUsersOrderBy():
    #创建连接池对象
    connpool = sessionmaker()

    #获取连接
    conn = connpool()

    #执行查询操作
    users = conn.query(User).order_by(User.userid.desc()).all()

    #断开连接
    conn.close()

    return users


# print queryUsersOrderBy()

def queryUsersCount():
    #创建连接池对象
    connpool = sessionmaker()

    #获取连接
    conn = connpool()

    #执行查询操作
    users = conn.query(User).count()

    #断开连接
    conn.close()

    return users


# print queryUsersCount()


def queryUsersPage(num,size=1):
    #创建连接池对象
    connpool = sessionmaker()

    #获取连接
    conn = connpool()

    #执行查询操作
    users = conn.query(User).offset((num-1)*size).limit(size).all()

    #断开连接
    conn.close()

    return users


# print queryUsersPage(3)


def queryUserByPk():
    #创建连接池对象
    connpool = sessionmaker()

    #获取连接
    conn = connpool()

    #执行查询操作
    users = conn.query(User).get(1)

    #断开连接
    conn.close()

    return users


print queryUserByPk()