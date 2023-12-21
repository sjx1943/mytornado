#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler, UIModule
import pymysql



class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        self.render('login.html')

    def post(self, *args, **kwargs):
        pass

class LoginHandler(RequestHandler):
    def initialize(self, conn):
        self.conn = conn

    def get(self, *args, **kwargs):

        self.render('login.html')
    def prepare(self):
        if self.request.method == 'POST':
            self.uname = self.get_argument('username')
            self.pwd = self.get_argument('password')


    def post(self, *args, **kwargs):
        cursor = self.conn.cursor()
        sql = 'select * from tb_user where user_name="%s" and user_password="%s"'%(self.uname,self.pwd)
        cursor.execute(sql)
        user = cursor.fetchone()
        if user:
            self.write('successdenglu')
        else:
            self.write('faildenglu')
    def set_default_headers(self) -> None:
        self.set_header("Server","SJXServer/1.0")
    def write_error(self,status_code, **kwargs):
        self.render('error.html')

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
dbconfig = dict(host="127.0.0.1",
                port=3306,
                user="root",
                password="19910403",
                database="xianyu_db",
                charset="utf8")

app = Application(handlers=[('/',IndexHandler),
                            ('/login',LoginHandler,{'conn':pymysql.connect(**dbconfig)}),
                            ('/upload',UploadHandler),
                            ('/re',GetRequestInfo),
                            ('/regist',RegistHandler,{'conn':pymysql.connect(**dbconfig)})],
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
