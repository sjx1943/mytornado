#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from urllib.parse import urlencode

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler, UIModule, StaticFileHandler
import pymysql


def reverse(obj):
    if isinstance(obj,list):
        obj.reverse()
    return obj

class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        self.render('mystatics.html')

    def post(self, *args, **kwargs):
        pass


class Person(object):
    def __init__(self,pname):
        self.name = pname


class TemplateHandler(RequestHandler):
    def get(self, *args, **kwargs):
        L = ['a1','a2','a3']
        D = {'k1':'v1','k2':'v2','k3':'v3'}
        P = Person('sjx')
        S1 = '<h1>china</h1>'
        S2 = '<script>location.href="https://www.baidu.com"</script>'
        self.render('template1.html',
                    rev=reverse, s1=S1,s2=S2,
                    title='mainPG',l=L,d=D,p=P)

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
        sql = 'SELECT * FROM tb_user WHERE uname=%s AND pwd=%s'
        cursor.execute(sql, (self.uname, self.pwd))
        user = cursor.fetchone()
        if user:
            # Use the username from the user object to display the personalized message
            self.write('你好，%s' % self.uname)
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
            r = '注册成功，返回登录'
        return self.render_string('mymodule/login_module.html',result=r)

class Registmodule(UIModule):
    def render(self, *args,**kwargs):
        print('regist_query---->', self.request.query)
        r = ''
        if self.request.query:
            r = '注册失败'
        return self.render_string('mymodule/register_module.html', result=r)


class RegistHandler(RequestHandler):
    def initialize(self,conn):
        self.conn = conn
    def get(self,*args,**kwargs):
        error_message = self.get_argument('error',None)
        self.render('reg.html',error = error_message)
    def post(self,*args,**kwargs):
        uname = self.get_argument('username', '').strip()  # Use strip() to remove leading/trailing whitespace
        pwd = self.get_argument('password', '').strip()
        city = self.get_argument('city', None)

        # Check if username or password is empty
        if not uname or not pwd:
            error_message = '用户名和密码不能为空'
            self.redirect('/regist?' + urlencode({'error': error_message}))
            return  # Return early to prevent further processing

        cursor = self.conn.cursor()
        sql = 'INSERT INTO tb_user (uname, pwd, city, create_time) VALUES (%s, %s, %s, NOW())'
        params = (uname, pwd, city)
        try:
            cursor.execute(sql, params)
            self.conn.commit()
            self.redirect('/login?success=1')
        except Exception as e:
            self.conn.rollback()
            error_message = str(e)
            if 'duplicate' in error_message.lower():
                error_message = '已有该用户'
            elif 'not null' in error_message.lower():
                error_message = '请输入完整'
            else:
                error_message = '其他数据库错误'
            self.redirect('/regist?注册失败：' + urlencode({'error': error_message}))



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

class Setcookie(RequestHandler):
    def get(self,*args,**kwargs):
        # #普通设置方式
        # self.set_cookie('uname','sjx',expires_days=3)
        #加密设置方式
        self.set_secure_cookie('uname','jiamisjx',expires_days=3)
    # def post(self,*args,**kwargs):

class Getcookie(RequestHandler):
    def get(self,*args,**kwargs):
        # #获取普通cookie
        # self.write(self.get_cookie('uname'))
        #获取加密cookie
        self.write(self.get_secure_cookie('uname'))



dbconfig = dict(host="127.0.0.1",
                port=3306,
                user="root",
                password="19910403",
                database="xianyu_db",
                charset="utf8")

#cookie_secret 对应键值的作用是加密cookie中的数据，默认为随机键值加密，安全考虑用固定键值
settings = {"static_path":os.path.join(os.path.dirname(__file__), "mystatics"),
            'template_path':os.path.join(os.path.dirname(__file__), "mytemplate"),
            "login_url":"/login", 'cookie_secret':'sjxxx','xsrf_cookies':True}

app = Application(handlers=[('/',IndexHandler),
                            ('/mystatics/(.*)',StaticFileHandler,dict(path=settings['static_path'])),
                            ('/moban',TemplateHandler),
                            ('/login',LoginHandler,{'conn':pymysql.connect(**dbconfig)}),
                            ('/upload',UploadHandler),
                            ('/re',GetRequestInfo),
                            ('/regist',RegistHandler,{'conn':pymysql.connect(**dbconfig)}),
                            ('/set',Setcookie),('/get',Getcookie)],
                  # template_path = 'mytemplate',
                  # static_path = 'mystatics',
                  ui_modules={'loginmodule':Loginmodule,
                              'blogmodule':Blogmodule,
                              'registmodule':Registmodule},**settings)





define('duankou',type=int,default = 8888)

parse_config_file('../config/config')

server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
