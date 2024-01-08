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
from sqlalchemy import create_engine,desc,Column
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql import func

# Update the connection URL to use PyMySQL (`+pymysql`)
conn_url = 'mysql+pymysql://root:19910403@localhost:3306/xianyu_db?charset=utf8'
engine = create_engine(conn_url, echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Test(Base):
    __tablename__ = 'test'
    userid = Column(Integer, primary_key=True, autoincrement=True)
    uname = Column(String(30), unique=True)
    pwd = Column(String(30))
    create_time = Column(DateTime,default=func.now())
    def __repr__(self):
        return "<Test(userid='%s',uname='%s',create_time='%s')>" % (self.userid,self.uname,self.create_time)
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
# Base.metadata.create_all(engine)


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
# insert_record('user1', 'password123')

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
    from sqlalchemy import and_
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













