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


# print queryUserByPk()

#提取公共部分成装饰器
def connwrapper(func):
    def _wrapper(*args,**kwargs):
        from sqlalchemy.orm import sessionmaker
        connpool = sessionmaker()
        conn = connpool()
        datas = func(conn,*args,**kwargs)
        conn.close()
        return datas
    return _wrapper

@connwrapper
def deleteUserById(conn,userid):
    conn.query(User).filter(User.userid==userid).delete()
    conn.commit()


# deleteUserById(5)


@connwrapper
def updateUser1(conn,userid):
    user = conn.query(User).get(userid)
    user.uname = 'zhangsan123'
    conn.commit()


# updateUser1(1)

@connwrapper
def updateUser2(conn,userid):
    conn.query(User).filter(User.userid==userid).update({User.uname:'zhangsan'})
    conn.commit()

# updateUser2(1)


@connwrapper
def queryNtable(conn):
    from sqlalchemy import and_,or_,not_

    # users = conn.query(User).filter(and_(User.uname=='zhangsan',User.pwd=='123123')).all()
    # users = conn.query(User).filter(or_(User.uname=='zhangsan',User.pwd=='234234')).all()
    users = conn.query(User).filter(not_(User.uname=='zhangsan')).all()



    return users


# print queryNtable()

@connwrapper
def groupByUsers(conn):
    from sqlalchemy.sql.functions import func
    users = conn.query(func.count(User.userid),User.pwd).group_by(User.pwd).all()


    return users

# print groupByUsers()


@connwrapper
def queryPartColumn(conn):
    users = conn.query(User.userid,User.uname).all()

    return users

print queryPartColumn()