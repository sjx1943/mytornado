#coding=utf-8

import torndb

def queryAll(cname):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')

    stus = conn.query('select * from t_cls,t_stu where t_cls.cname="%s" and t_cls.cno=t_stu.cls'%cname)

    conn.close()

    return stus

# print queryAll('Python201班')


def deleteByParams(cno):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    conn.execute('delete from t_cls where cno="%s"'%cno)

    conn.close()

deleteByParams(1)




