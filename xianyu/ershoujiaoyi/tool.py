#!/usr/bin/env python
# -*- coding: utf-8 -*-
# tornado框架数据库操作示例
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
# 多行插入
def inserDatas(args=[]):
    conn = pymysql.connect(**dbconfig)
    #用连接对象创建游标对象
    cursor = conn.cursor()
    sql = 'insert into test values(null,"%s","%s")'
    cursor.executemany(sql,args)
    conn.commit()
    conn.close()
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

# inserData('hangzhou','zhejiang')
# inserDatas([('nanjing','jiangsu'),('lasa','xizang')])
# print(queryDatas())
# print(queryDatasByParams('tx','bj'))
# print(queryDatasBylike('u'))