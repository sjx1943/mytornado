#coding=utf-8
import torndb

def insertNTable(cname,sname,coursenames=[]):
    conn = torndb.Connection(host='127.0.0.1',database='db01', user='root', password='123456')

    #确定班级表是否有数据
    cls = conn.query('select cno from t_cls where cname="%s"'%cname)
    if not cls:
        cno = conn.insert('insert into t_cls values(null,"%s")'%cname)
    else:
        cno = cls[0]['cno']

    #确定学生表是否有数据
    stu = conn.query('select sno from t_stu where sname="%s"'%sname)
    if not stu:
        sno = conn.insert('insert into t_stu values(null,"%s","%s")'%(sname,cno))
    else:
        sno = stu[0]['sno']


    #确定课程表中是否有数据
    courseIdList = []

    for cn in coursenames:
        course = conn.query('select courseid from t_course where coursename="%s"'%cn)
        if not course:
            courseid = conn.insert('insert into t_course values(null,"%s")'%cn)
            courseIdList.append(courseid)
        else:
            courseid = course[0]['courseid']
            courseIdList.append(courseid)



    #确定中间表中有数据

    for ci in courseIdList:
        conn.insert('insert into t_sc values(null,"%s","%s")'%(sno,ci))



insertNTable('Python201班','zhangsan',['H5','Python'])