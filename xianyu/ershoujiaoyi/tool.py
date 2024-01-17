#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tornado框架数据库直连操作示例,操作表为test表
"""
import pymysql

dbconfig = dict(host="127.0.0.1",
                port=3306,
                user="root",
                password="19910403",
                database="xianyu_db",
                charset="utf8")

# 单行插入
def inserData(city,pro):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'insert into test values(null,"%s","%s")' % (city,pro)
    cursor.execute(sql)
    conn.commit()
    conn.close()
    # inserData('hangzhou','zhejiang')

# 多行插入
def inserDatas(args=[]):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'insert into test values(null,"%s","%s")'
    cursor.executemany(sql,args)
    conn.commit()
    conn.close()
    # inserDatas([('nanjing','jiangsu'),('lasa','xizang')])

# 单表全量查询
def queryDatas():
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'select * from test'
    cursor.execute(sql)
    msg = cursor.fetchall()
    conn.close()
    return msg
# print(queryDatas())

# 条件查询
def queryDatasByParams(cid,city):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'select * from test where cid="%s" and city="%s"'%(cid,city)
    cursor.execute(sql)
    msg = cursor.fetchall()
    conn.close()
    return msg
# print(queryDatasByParams('tx','bj'))

# 模糊查询,%%代表通配，例中输出以‘u'为结尾的结果
def queryDatasBylike(x):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'select * from test where cid like "%%{re}"'.format(re=x)
    cursor.execute(sql)
    msg = cursor.fetchall()
    conn.close()
    return msg
# print(queryDatasBylike('u'))

#分页,num代表第几页，size代表每页行数
def query_all_page(num,size):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'select * from test limit %s,%s'%((num-1)*size,size)
    cursor.execute(sql)
    msg = cursor.fetchall()
    conn.close()
    return msg
#print(fenye(2,3))

#更新单条数据
def update(cid,newcity):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'update test set city="%s" where cid="%s"'%(newcity,cid)
    cursor.execute(sql)
    conn.commit()
    conn.close()
#update('jd','shanghai')

#删除单行数据
def delete(cid):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'delete from test where cid="%s"'%(cid)
    cursor.execute(sql)
    conn.commit()
    conn.close()
#delete('tx')


"""
tornado框架数据库ORM操作示例,采用第三方组件
"""

import sqlalchemy
from sqlalchemy import create_engine, desc, Column, text, ForeignKey,and_
from sqlalchemy.orm import declarative_base, sessionmaker,joinedload
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql import func



# Update the connection URL to use PyMySQL (`+pymysql`)
conn_url = 'mysql+pymysql://root:19910403@localhost:3306/xianyu_db?charset=utf8mb4'
engine = create_engine(conn_url, echo=False,pool_recycle=3600)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Test(Base):
    __tablename__ = 'tb_user'
    userid = Column(Integer, primary_key=True, autoincrement=True)
    uname = Column(String(30), unique=True, nullable=False)
    pwd = Column(String(30))
    city = Column(String(10))
    create_time = Column(DateTime,default=func.now())
    def __repr__(self):
        return "<Test(userid='%s',uname='%s',create_time='%s')>" % (self.userid,self.uname,self.create_time)
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)


#提取公共部分形成装饰器
def connwrapper(func):
    def _wrapper(*args, **kwargs):

        try:
            datas = func(session, *args, **kwargs)
            session.commit()  # 确保操作提交
        except Exception as e:
            session.rollback()  # 如果出现异常，回滚
            raise e
        finally:
            session.close()  # 确保连接最终关闭
        return datas
    return _wrapper

#----------------------增类------------------------------
# Insert a single record
@connwrapper
def insert_record(session,uname, pwd):
        new_record = Test(uname=uname, pwd=pwd)
        session.add(new_record)
        return new_record.userid  # Return the primary key of the new record
# insert_record('user2', 'password123')

# Insert multiple records
@connwrapper
def insert_multiple_records(session,records):
        new_records = [Test(uname=record['uname'], pwd=record['pwd']) for record in records]
        session.add_all(new_records)
        return [record.userid for record in new_records]  # Return primary keys of new records
# insert_multiple_records([{'uname': 'user9', 'pwd': 'password234'}, {'uname': 'user10', 'pwd': 'password345'}])

#----------------------查类------------------------------
# Query records with sorting
@connwrapper
def query_records_sorted_by(session,column_name, descending=False):
    if descending:
        results = session.query(Test).order_by(desc(column_name)).all()
    else:
        results = session.query(Test).order_by(column_name).all()

    return [{k:v for k,v in row.__dict__.items() if k != '_sa_instance_state'} for row in results]

# sorted_records =  query_records_sorted_by('userid', descending=True)
# for re in sorted_records:
#     print(re)

# Query a record by primary key
@connwrapper
def query_by_primary_key(session,cls,pk):
        record = session.get(cls,pk)
        if record:
            return {k:v for k,v in record.__dict__.items() if k != '_sa_instance_state'}
        else:
            return None
# record = query_by_primary_key(Test,6)
# print(record)


# Get the count of records in a table
@connwrapper
def count_records(session):
    return session.query(Test).count()
# record_count = count_records()
# print(record_count)
# Pagination function


@connwrapper
def paginate_records(session,page, page_size):
    offset = (page - 1) * page_size
    results = session.query(Test).offset(offset).limit(page_size).all()
    return [{k:v for k,v in row.__dict__.items() if k != '_sa_instance_state'} for row in results]
# paginated_records = paginate_records(1, 3)
# for re in paginated_records:
#     print(re)

# 使用装饰器实现查询指定uname的行数据，行数据不包含对象字段
@connwrapper
def filter1(session, value):
    record = session.query(Test).filter(Test.uname == value).all()
    if record:
        return [{k: v for k, v in row.__dict__.items() if k != '_sa_instance_state'} for row in record]
    else:
        return "no results"
    # Convert the ORM objects to dictionaries

# print(filter1('zhangsan'))

# 使用装饰器实现查询指定uname和pwd的行数据
@connwrapper
def filter_and(session,un,pwd):

    results = session.query(Test).filter(and_(Test.uname == un,Test.pwd == pwd)).all()
    return [row.__dict__ for row in results]
# print(filter_and('zhangsan','122'))

# 使用装饰器实现查询指定uname或pwd的行数据，行数据不含对象和pwd字段
@connwrapper
def filter_or(session,un,pwd):
    from sqlalchemy import or_
    results = session.query(Test).filter(or_(Test.uname == un,Test.pwd == pwd)).all()
    return [{k:v for k,v in row.__dict__.items() if k != '_sa_instance_state' and k != 'pwd'} for row in results]

# results = filter_or('zhangsan','password123')
# for re in results:
#     print(re)

# 使用装饰器实现查询指定uname不等于zhangsan的行数据，行数据只有uname字段
@connwrapper
def filter_not(session,un):
    from sqlalchemy import not_
    results = session.query(Test).filter(not_(Test.uname == un)).all()
    return [{k:v for k,v in row.__dict__.items() if k=='uname'} for row in results]
# results = filter_not('zhangsan')
# for re in results:
#     print(re)
# 使用装饰器实现嵌套查询，指定uname不等于zhangsan且pwd不等于password123的行数据，行数据只有uname字段
@connwrapper
def filter_qiantao(session,un,pwd):
    from sqlalchemy import not_,or_
    results = session.query(Test).filter(not_(or_(Test.uname == un,Test.pwd == pwd))).all()
    return [{k:v for k,v in row.__dict__.items() if k=='uname'} for row in results]
# results = filter_qiantao('zhangsan','password123')
# for re in results:
#     print(re)

# 使用装饰器实现分组查询，查询不同pwd的个数
@connwrapper
def group_by_query(session):
    from sqlalchemy import func
    results = session.query(func.count(Test.userid),Test.pwd).group_by(Test.pwd).all()
    return results
# print(group_by_query())

# 使用装饰器实现查看部分字段,如userid和uname
@connwrapper
def queryPartColumn(session):
    re=session.query(Test.userid,Test.uname).all()
    return re
# print(queryPartColumn())

# 使用装饰器实现查看所有字段
@connwrapper
def query_all_records(session):
    results = session.query(Test).all()
    return [{k:v for k,v in row.__dict__.items() if k != '_sa_instance_state'} for row in results]
# results = query_all_records()
# for re in results:
#     print(re)


#----------------------删类------------------------------
# 使用装饰器实现删除指定userid行数据数据
@connwrapper
def deleteUserById(conn, userid):
    # 使用Session对象查询用户并删除
    user_to_delete = conn.query(Test).filter(Test.userid == userid).first()
    if user_to_delete:
        conn.delete(user_to_delete)
        return f"User with id {userid} has been deleted."
    else:
        return f"No user found with id {userid}."
#deleteUserById(userid=3)

#----------------------改类------------------------------
# 使用装饰器实现更新指定userid行的uname字段数据
@connwrapper
def updateUser(session, user_id, newvalue):
    user = session.query(Test).filter_by(userid=user_id).one()
    user.uname = newvalue
# updateUser(1,'zhangsan')

"""
多表ORM操作示例,采用第三方组件
"""
class Clazz(Base):
    __tablename__ = 't_cls'
    cno = Column(Integer, primary_key=True, autoincrement=True)
    cname = Column(String(30), unique=True, nullable=False)
    def __repr__(self):
        return "<Clazz(class_name='%s')>" % (self.cname)
class Student(Base):
    __tablename__ = 't_stu'
    sno = Column(Integer, primary_key=True, autoincrement=True)
    sname = Column(String(30), unique=True, nullable=False)
    cno = Column(Integer, ForeignKey('t_cls.cno',ondelete='CASCADE'))
    def __repr__(self):
        return "<Student(people_name='%s')>" % (self.sname)
class Course(Base):
    __tablename__ = 't_course'
    courseid = Column(Integer, primary_key=True, autoincrement=True)
    coursename = Column(String(30), unique=True, nullable=False)
    def __repr__(self):
        return "<Course(course_name='%s')>" % (self.coursename)
class Middle(Base):
    __tablename__ = 't_sc'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sno = Column(Integer, ForeignKey('t_stu.sno',ondelete='CASCADE'))
    courseid = Column(Integer, ForeignKey('t_course.courseid',ondelete='CASCADE'))
#
# if __name__ == '__main__':
#     Base.metadata.create_all(engine)
# #
#
@connwrapper
def insertDatas(session, cname, sname, coursenames):
    # Insert into Clazz
    new_class = Clazz(cname=cname)
    session.add(new_class)
    session.flush()  # Flush to get the generated ID for the class

    # Insert into Student
    new_student = Student(sname=sname, cno=new_class.cno)
    session.add(new_student)
    session.flush()  # Flush to get the generated ID for the student

    # Insert into Course and Middle
    for coursename in coursenames:
        # Check if the course already exists
        existing_course = session.query(Course).filter_by(coursename=coursename).first()
        if not existing_course:
            # If the course does not exist, create a new one
            new_course = Course(coursename=coursename)
            session.add(new_course)
            session.flush()  # Flush to get the generated ID for the course
            course_id = new_course.courseid
        else:
            # If the course exists, use the existing ID
            course_id = existing_course.courseid

        # Insert into Middle table
        new_middle = Middle(sno=new_student.sno, courseid=course_id)
        session.add(new_middle)

    # Return some kind of success indicator or the created objects
    return {"class": new_class, "student": new_student, "courses": coursenames}

# Call the function
# You would use the function like this:
# insertDatas('class11', 'Mary', ['C++'])


def queryALL():
    def process_results(query_results):
        processed_results = []
        for result in query_results:
            if hasattr(result, '__dict__'):
                # It's an ORM object; convert it to a dictionary.
                obj_dict = result.__dict__.copy()
                obj_dict.pop('_sa_instance_state', None)
                processed_results.append(obj_dict)
            elif isinstance(result, tuple):
                # Check if the tuple contains ORM objects
                if all(hasattr(item, '__dict__') for item in result):
                    # It's a tuple of ORM objects; convert each to a dictionary.
                    combined_dict = {}
                    for item in result:
                        obj_dict = item.__dict__.copy()
                        obj_dict.pop('_sa_instance_state', None)
                        combined_dict.update(obj_dict)
                    processed_results.append(combined_dict)
                else:
                    # It's a raw SQL result; assume the tuple is structured with known schema
                    # You need to define the column names that correspond to your SQL query's result
                    column_names = ['column1', 'column2']  # Replace with actual column names
                    row_as_dict = {column_names[i]: column for i, column in enumerate(result)}
                    processed_results.append(row_as_dict)
            else:
                # Handle other types of results if necessary.
                pass  # Replace with appropriate handling code if needed.
        return processed_results

    try:
        # 执行各种查询
        cross_join = session.query(Student, Clazz).all()
        equi_join = session.query(Student).join(Clazz, Student.cno == Clazz.cno).all()
        non_equi_join = session.query(Student).join(Clazz, and_(Student.cno == Clazz.cno,Clazz.cno<3,)).all()
        inner_join = session.query(Student).join(Clazz).filter(Student.cno == Clazz.cno).all()
        left_outer_join = session.query(Student).outerjoin(Clazz, Student.cno == Clazz.cno).all()
        native_sql_query = session.execute(text("SELECT * FROM t_cls")).fetchall()
        # print('查看原始结果1',cross_join)
        # print('查看原始结果2', native_sql_query)
        # 处理查询结果
        results = {
            "cross_join": process_results(cross_join),
            "equi_join": process_results(equi_join),
            "non_equi_join": process_results(non_equi_join),
            "inner_join": process_results(inner_join),
            "left_outer_join": process_results(left_outer_join),
            "native_sql": process_results(native_sql_query)
        }

    finally:
        session.close()

    # 打印结果
    for key, value in results.items():
        print(f"{key}:")
        for item in value:
            print(item)

    return results


# 调用函数进行查询
# queryALL()



