#coding=utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
import MySQLdb


def _getConn():
    return MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',db='db01',port=3306)

class RegisterHandler(RequestHandler):
    def initialize(self,conn):
        self.conn = conn

    def get(self, *args, **kwargs):
        self.render('templates/register.html')

    def post(self, *args, **kwargs):
        #获取请求参数
        uname = self.get_argument('uname')
        pwd = self.get_argument('pwd')


        try:
            cursor = self.conn.cursor()
            cursor.execute('insert into t_user values(null,"%s","%s",now())'%(uname,pwd))
            self.conn.commit()
            self.write('注册成功！')
        except Exception as e:
            self.conn.rollback()
            self.write('注册失败！')



app = Application([
    (r'/register/',RegisterHandler,{'conn':_getConn()})
])


if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()