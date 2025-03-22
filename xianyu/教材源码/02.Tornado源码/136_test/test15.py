#coding=utf-8

import torndb

def insertData(uname,pwd):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    conn.insert('insert into t_user values(null,"%s","%s",now())'%(uname,pwd))
    conn.close()

# insertData('lisi','123')


def insertDatas(args=[]):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'insert into t_user values(null,%s,%s,now())'
    conn.insertmany(sql,args)
    conn.close()


# insertDatas([('wangwu','123'),('zhaoliu','123')])

def queryDatas():
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user'
    users = conn.query(sql)
    conn.close()
    return users

# print queryDatas()

def queryDataByParams(uname,pwd):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user where uname="%s" and pwd="%s"'%(uname,pwd)
    users = conn.query(sql)
    conn.close()
    return users


# print queryDataByParams('zhangsan','123')


def queryDatasByLike(uname):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user where uname like "%%{ua}"'.format(ua=uname)
    users = conn.query(sql)
    conn.close()
    return users


print queryDatasByLike('i')