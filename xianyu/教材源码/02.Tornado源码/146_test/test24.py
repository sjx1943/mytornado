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



def insertDatas(cname,sname,coursenames=[]):
    from sqlalchemy.orm import sessionmaker
    #创建连接池对象
    connpool = sessionmaker()
    #获取连接
    conn = connpool()
    #确定班级表中是否存在数据
    cls = conn.query(Clazz.cno).filter(Clazz.cname==cname).all()

    if not cls:
        cls1 = Clazz(cname=cname)
        conn.add(cls1)
        conn.commit()
        conn.refresh(cls1)
        cno = cls1.cno


    else:
        cno = cls[0]


    #确定学生表中是否存在数据
    stu = conn.query(Student.sno).filter(Student.sname==sname).all()

    if not stu:
        stu1 = Student(sname=sname,cls=cno)
        conn.add(stu1)
        conn.commit()
        conn.refresh(stu1)
        sno = stu1.sno

    else:
        sno = stu[0]

    #确定课程表中是否存在数据
    courseIdList = []

    for cn in coursenames:
        course = conn.query(Course.courseid).filter(Course.coursename==cn).all()
        if not course:
            course1 = Course(coursename=cn)
            conn.add(course1)
            conn.commit()
            conn.refresh(course1)
            courseIdList.append(course1.courseid)
        else:
            courseIdList.append(course[0])

    #确定中间表中是否存在数据
    for ci in courseIdList:
        sc = SC(sno=sno,courseid=ci)
        conn.add(sc)
        conn.commit()
        conn.refresh(sc)


    conn.close()

    print '执行结束'


insertDatas(cname='B201Python',sname='lisi',coursenames=['H5','Python'])
