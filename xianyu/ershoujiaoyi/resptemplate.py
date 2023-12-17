#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler, UIModule
import pymysql
"""
host – Host where the database server is located
user – Username to log in as
password – Password to use.
database – Database to use, None to not use a particular one.
port – MySQL port to use, default is usually OK. (default: 3306)
unix_socket – Optionally, you can use a unix socket rather than TCP/IP.
charset – Charset you want to use.
sql_mode – Default SQL_MODE to use.
read_default_file – Specifies my.cnf file to read these parameters from under the [client] section.
conv –
"""

def _getConn():
    settings = {"host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "19910403",
                "database": "xianyu_db",
                "charset": "utf8"
                }
    return pymysql.connect(**settings)

class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        self.render('login.html')

    def post(self, *args, **kwargs):
        pass

class LoginHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('login.html')
    def post(self, *args, **kwargs):
        ua = self.get_body_argument('username', None)
        #通用方法get_argument
        ps = self.get_argument('password', None)
        favs = self.get_body_arguments('fav',None)

        if ua == 'admin' and ps == '123456':
            self.write(u'登录成功')
        else:
            self.write(u'登录失败')
        # #输出到页面显示
        # self.write('username is %s, password is %s, favs is %s' % (ua, ps, favs))

class UploadHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('upload.html')
    def post(self, *args, **kwargs):
        #获取上传文件的信息
        #[{filename:xxx, body:xxx, content_type:xxx},{}}]

        img1 = self.request.files['img1']
        for img in img1:
            body = img['body']
            content_type = img['content_type']
            filename = img['filename']
        print(content_type)
        with open(os.path.join(os.getcwd(),'files',filename),'wb') as f:
            f.write(body)
        #告诉浏览器如何解析,本例是图片image/png
        self.set_header('Content-Type',content_type)
        self.write(body)


class GetRequestInfo(RequestHandler):
    def get(self, *args, **kwargs):
        protocol = self.request.protocol
        method = self.request.method
        uri = self.request.uri
        ua = self.request.headers['User-Agent']
        # self.write('%s,%s,%s,%s' % (protocol,ua,uri,method))
        # 重定向
        # self.set_status(302)
        # self.set_header('location', 'https://www.baidu.com')
        #设置响应
        # self.set_status(666)
        self.set_header('Server','sggServer')

    def post(self,*args,**kwargs):
        pass

class Loginmodule(UIModule):
    def render(self,*args,**kwargs):
        # return 'zifuchuan'
        # print(self.request)
        # print(self.request.uri)
        # print(self.request.path)
        # print(self.request.query)
        r=''
        if self.request.query:
            r = '用户名或密码错误'
        return self.render_string('mymodule/login_module.html',result=r)

class Registmodule(UIModule):
    def render(self, *args,**kwargs):
        print('regist_query---->', self.request.query)
        r = ''
        if self.request.query:
            err = self.request.query.split("=")[1]
            if err == 'empty':
                r = '请输入完整'
            if err == 'duplicate%20error':
                r = '已有该用户'
            if err == 'other dberror':
                r = '其他数据库错误'
        return self.render_string('mymodule/regist_module.html',result=r)
class RegistHandler(RequestHandler):

    def initialize(self,conn):
        self.conn = conn


    def get(self,*args,**kwargs):
        self.render('regist.html')
    def post(self,*args,**kwargs):
        uname = self.get_argument('username')
        pwd = self.get_argument('password')
        city = self.get_argument('city',None)
        cursor = self.conn.cursor()
        sql = 'insert into tb_user values(null,"%s","%s",NULL,"%s",now(),null)'%(uname,pwd,city)

        # params = (uname, pwd, city)
        try:
            cursor.execute(sql)
            # cursor.connection.commit()
            # cursor.execute('insert into tb_user values(NULL,"%s","%s",NULL,"%s",now(),NULL'%(uname,pwd,city))
            self.conn.commit()
            self.write("success!")
        except Exception as e:
            self.conn.rollback()
            self.write("fail!")

class Blogmodule(UIModule):
    def render(self,*args,**kwargs):
        return self.render_string('mymodule/blog_module.html',blogs = [{
                        'author':'Tom',
                        'avatar':'a.jpeg',
                        'title':'living',
                        'content':'how life is going on the earth',
                        'tags':'bio',
                        'count': 9
                    },{
                        'author':'John',
                        'avatar': 'fevicon.png',
                        'title':'what is chatgpt',
                        'content':'chatgpt is xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                        'tags':'IT',
                        'count': 0
                    },{
                        'author':'Jordan',
                        'avatar': None,
                        'title':'food',
                        'content':'the most delicious food in the world is xxxxxxxxxxxxxxxxx',
                        'tags':'bio',
                        'count': 3
                    }])
app = Application(handlers=[('/',IndexHandler),
                            ('/login',LoginHandler),
                            ('/upload',UploadHandler),
                            ('/re',GetRequestInfo),
                            ('/regist',RegistHandler,{'conn':_getConn()})],
                  template_path = 'mytemplate',
                  static_path = 'mystatics',
                  ui_modules={'loginmodule':Loginmodule,
                              'blogmodule':Blogmodule,
                              'registmodule':Registmodule})





define('duankou',type=int,default = 8888)

parse_config_file('../config/config')

server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
