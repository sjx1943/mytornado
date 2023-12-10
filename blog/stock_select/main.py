#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import time
from os import remove

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler, UIModule
import pymysql

from ershoujiaoyi.util.myutil import mymd5


class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        r=''
        msg = self.get_query_argument('msg', None)
        if msg:
            r = '用户名or密码错误'
        self.render('login.html',result=r)



    def post(self, *args, **kwargs):
        pass

class LoginHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass
    def post(self, *args, **kwargs):
        ua = self.get_body_argument('username', None)
        ps = self.get_body_argument('password', None)
        settings = {"host":"127.0.0.1",
                    "port":3306,
                    "user":"root",
                    "password":"19910403",
                    "database":"blog_db",
                    "charset":"utf8"
                    }
        connection = pymysql.connect(**settings)
        cursor = connection.cursor()

        sql = 'select count(*) from tb_user where user_name = %s' \
              'and user_password = %s'
        #让密码变为真正的密码
        pwd = mymd5(ps)
        params = (ua,pwd)

        cursor.execute(sql,params)

        # result = cursor.fetchall()
        result = cursor.fetchone()
        print('result-------->: ',result)

        if result[0]:
            self.redirect('/blog?username='+ua)
        else:
            #跳转回登陆界面
            self.redirect('/?msg=fail')



class StockHandler(RequestHandler):
    def get(self, *args, **kwargs):
        context = {'code':'ABBNY'}
        self.render('index.html', **context)

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

class RegistHandler(RequestHandler):
    def get(self,*args,**kwargs):
        self.render('regist.html')

    def post(self,*args,**kwargs):
        ua = self.get_body_argument('username')
        ps = self.get_body_argument('password')
        city = self.get_body_argument('city',None)
        if ua and ps and city:
            avatar = None
            if self.request.files:
                f = self.request.files['avatar'][0]
                body = f['body']
                fname = str(time.time())+f['filename']
                writer = open('mystatics/images/%s' % fname, 'wb')
                avatar = fname
                writer.write(body)
                writer.close()
            settings = {"host":"127.0.0.1",
                        "port":3306,
                        "user":"root",
                        "password":"19910403",
                        "database":"blog_db",
                        "charset":"utf8"
                        }
            connection = pymysql.connect(**settings)
            cursor = connection.cursor()
            sql = 'insert into tb_user(user_name,user_password,user_avatar,user_city)' \
                  'values(%s,%s,%s,%s)'
            # md = hashlib.md5()
            # md.update(ps.encode('utf8'))
            # #转16进制
            # pwd = md.hexdigest()
            pwd = mymd5(ps)

            params = (ua,pwd,avatar,city)
            try:
                cursor.execute(sql,params)
                cursor.connection.commit()
            except Exception as e:
                if avatar:
                    remove('mystatics/image/%s'%avatar)
                err = str(e)
                code = err.split(',')[0].split('(')[1]
                r=''
                if code == '1062':
                    r = 'duplicate error'
                    self.redirect('/regist?msg=' + r)
                else:
                    r = 'other dberror'
                    self.redirect('/regist?msg='+r)


            else:
                self.redirect('/')

        else:

            self.redirect('/regist?msg=empty')



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
                            ('/stock',StockHandler),
                            ('/login',LoginHandler),
                            ('/regist',RegistHandler)],
                  template_path = 'mytemplate',
                  static_path = 'mystatics',
                  static_url_prefix='/static',
                  ui_modules={'loginmodule':Loginmodule,
                              'blogmodule':Blogmodule,
                              'registmodule':Registmodule},)


define('duankou',type=int,default = 8888)

parse_config_file('../config/config')

server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
