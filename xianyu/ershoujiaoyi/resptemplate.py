#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler, UIModule


class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        self.render('login.html')

    def post(self, *args, **kwargs):
        pass

class LoginHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass
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

class RegistHandler(RequestHandler):
    def get(self,*args,**kwargs):
        self.render('regist.html')

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
                            ('/regist',RegistHandler)],
                  template_path = 'mytemplate',
                  static_path = 'mystatics',
                  ui_modules={'loginmodule':Loginmodule,
                              'blogmodule':Blogmodule},)


define('duankou',type=int,default = 8888)

parse_config_file('../config/config')

server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
