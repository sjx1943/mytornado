#coding=utf-8

import torndb



def queryDatasByLike(uname):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user where uname like "%%{ua}"'.format(ua=uname)
    users = conn.query(sql)
    conn.close()
    return users


# print queryDatasByLike('i')


def queryDatasOrderBy(column):
    rule = 'ASC'

    if column.startswith('-'):
        rule = 'DESC'
        column = column[1:]


    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user order by %s %s'%(column,rule)

    users = conn.query(sql)
    conn.close()
    return users



# print queryDatasOrderBy('userid')


def queryDatasByPage(num,size=2):

    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')
    sql = 'select * from t_user limit %s,%s'%((num-1)*size,size)

    users = conn.query(sql)
    conn.close()
    return users


# print queryDatasByPage(1)

def updateUserByParams(uname,userid):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')

    sql = 'update t_user set uname="%s" where userid="%s"'%(uname,userid)

    conn.update(sql)

    conn.close()

# updateUserByParams('zhangjie',1)



def deleteUserByParams(userid):
    conn = torndb.Connection(host='127.0.0.1', database='db01', user='root', password='123456')

    sql = 'delete from t_user where userid="%s"'%userid

    conn.execute(sql)

    conn.close()


deleteUserByParams(1)