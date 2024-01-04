#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tornado框架数据库直连操作示例,操作表为test表
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

# tornado框架数据库ORM操作示例,采用第三方组件
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


# Insert a single record
def insert_record(uname, pwd):
    with Session() as session:
        new_record = Test(uname=uname, pwd=pwd)
        session.add(new_record)
        session.commit()
        return new_record.userid  # Return the primary key of the new record
# insert_record('user6', 'password123')

# Insert multiple records
def insert_multiple_records(records):
    with Session() as session:
        new_records = [Test(uname=record['uname'], pwd=record['pwd']) for record in records]
        session.add_all(new_records)
        session.commit()
        return [record.userid for record in new_records]  # Return primary keys of new records
# insert_multiple_records([{'uname': 'user4', 'pwd': 'password234'}, {'uname': 'user5', 'pwd': 'password345'}])

# Query all records in a table
def query_all_records():
    with Session() as session:
        return session.query(Test).all()
# all_records = query_all_records()
# print(all_records)

# Query records with sorting
def query_records_sorted_by(column_name, descending=False):
    with Session() as session:
        if descending:
            return session.query(Test).order_by(desc(column_name)).all()
        else:
            return session.query(Test).order_by(column_name).all()
# sorted_records =  query_records_sorted_by('userid', descending=True)
# print(sorted_records)

# Get the count of records in a table
def count_records():
    with Session() as session:
        return session.query(Test).count()
# record_count = count_records()
# print(record_count)
# Pagination function
def paginate_records(page, page_size):
    with Session() as session:
        offset = (page - 1) * page_size
        return session.query(Test).offset(offset).limit(page_size).all()
# paginated_records = paginate_records(1, 3)
# print(paginated_records)


# Query a record by primary key
def query_by_primary_key(cls,pk):
    with Session() as session:
        record = session.get(cls,pk)
        return record

# record = query_by_primary_key(Test,3)
# print(record)






