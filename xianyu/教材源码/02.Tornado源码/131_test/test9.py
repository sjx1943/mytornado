#coding=utf-8


from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
import pymysql

class LoginHandler(RequestHandler):

    def initialize(self,conn):
        self.conn = conn

    def prepare(self):
        if self.request.method == 'POST':
            self.uname = self.get_argument('uname')
            self.pwd = self.get_argument('pwd')

#实现错误自动跳转到指定页面
    def get(self, *args, **kwargs):
        1/0
        self.render('templates/login1.html')

    def post(self, *args, **kwargs):
        #获取游标对象
        cursor = self.conn.cursor()
        #执行SQL语句
        sql = "select * from tb_user where uname='%s' and pwd='%s'" % (self.uname, self.pwd)
        cursor.execute(sql)

        #获取执行结果
        user = cursor.fetchall()
        #判断是否登录成功
        if user:
            self.write('登录成功喽！')
        else:
            self.write('登录失败！')


    def set_default_headers(self):
        self.set_header('Server','SXTServer/1.1')


    def write_error(self, status_code, **kwargs):
        self.render('templates/error.html')





dbconfig=dict(host='127.0.0.1',user='sjx',passwd='19910403',db='db01',port=3306)


app = Application([
    (r'/login',LoginHandler,{'conn':pymysql.connect(**dbconfig)})
])

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()