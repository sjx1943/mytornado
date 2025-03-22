#coding=utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
import pymysql


def _getConn():
    return pymysql.connect(host='127.0.0.1',user='sjx',passwd='19910403',db='db01',port=3306)

class RegisterHandler(RequestHandler):
    def initialize(self,conn):
        self.conn = conn

    def get(self, *args, **kwargs):
        self.render('templates/register.html')

    def post(self, *args, **kwargs):
        #获取请求参数
        uname = self.get_argument('uname')
        pwd = self.get_argument('pwd')

        cursor = self.conn.cursor()
        sql = 'insert into tb_user (uname, pwd) VALUES (%s, %s)'
        params = (uname, pwd)
        try:

            cursor.execute(sql,params)
            self.conn.commit()
            self.write('注册成功！')
        except Exception as e:
            print(e)
            self.conn.rollback()
            self.write('注册失败！')



app = Application([
    (r'/register/',RegisterHandler,{'conn':_getConn()})
])


if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()