#coding=utf-8

from sqlalchemy.engine import create_engine

#1.配置引擎
conn_url = 'mysql://root:123456@127.0.0.1:3306/db01?charset=utf8'
engine = create_engine(conn_url,encoding='utf-8',echo=True)

#声明ORM基类
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(bind=engine)

#引入字段类型
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer,String,Date,DateTime,Float,Text


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



def queryAll():
    from sqlalchemy.orm import sessionmaker
    connpool = sessionmaker(bind=engine)
    conn = connpool()

    #交叉连接
    # users = conn.query(Student,Clazz).all()
    #等值连接
    # users = conn.query(Student,Clazz).filter(Student.cls==Clazz.cno).all()
    #非等值连接
    # users = conn.query(Student,Clazz).filter(Clazz.cno<3,Student.cls==Clazz.cno).all()

    #外连接（只支持左外连接）
    # users = conn.query(Clazz,Student).outerjoin(Student,Clazz.cno==Student.cls).all()

    sql = 'select * from t_cls'
    users = conn.execute(sql)

    conn.close()
    return users

# print queryAll()
print queryAll().fetchall()
