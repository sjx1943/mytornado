#coding=utf-8

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
import pymysql
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer,String,Date,DateTime,Float,Text


# Update the connection URL to use PyMySQL (`+pymysql`)
# conn_url = 'mysql+pymysql://sjx:19910403@localhost:3306/db01?charset=utf8mb4'
# engine = create_engine(conn_url, echo=True, pool_recycle=3600)
#
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()
#
# class Test(Base):
#     __tablename__ = 'tb_user1'
#     userid = Column(Integer, primary_key=True, autoincrement=True)
#     uname = Column(String(30), unique=True, nullable=False)
#     pwd = Column(String(30))
#     city = Column(String(10))
#     create_time = Column(DateTime,default=func.now())
#     def __repr__(self):
#         return "<Test(userid='%s',uname='%s',create_time='%s')>" % (self.userid,self.uname,self.create_time)
# # Create all tables in the engine. This is equivalent to "Create Table"
# # statements in raw SQL.
# Base.metadata.create_all(engine)



#1.配置引擎
conn_url = conn_url = 'mysql+pymysql://sjx:19910403@localhost:3306/db01?charset=utf8mb4'
engine = create_engine(conn_url, echo=True, pool_recycle=3600)
Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()
#声明ORM基类


#引入字段类型


#自定义模型类
class Clazz(Base):
    __tablename__='t_cls'

    cno = Column(Integer,primary_key=True,autoincrement=True)
    cname = Column(String(length=30),unique=True,nullable=False)


    def __repr__(self):
        return u'<Clazz:%s>'%self.cname



class Student(Base):
    __tablename__='t_stu'

    sno = Column(Integer,primary_key=True,autoincrement=True)
    sname = Column(String(length=30),unique=True,nullable=False)
    cls = Column(Integer,ForeignKey(Clazz.cno,ondelete='CASCADE'))


    def __repr__(self):
        return u'<Student:%s>'%self.sname


class Course(Base):
    __tablename__='t_course'

    courseid = Column(Integer,primary_key=True,autoincrement=True)
    coursename = Column(String(length=30),unique=True)

    def __repr__(self):
        return u'<Course:%s>'%self.coursename


class SC(Base):
    __tablename__='t_sc'

    id = Column(Integer,primary_key=True,autoincrement=True)
    sno = Column(Integer,ForeignKey(Student.sno,ondelete='CASCADE'))
    courseid = Column(Integer,ForeignKey(Course.courseid,ondelete='CASCADE'))



if __name__ == '__main__':
    Base.metadata.create_all(engine)
