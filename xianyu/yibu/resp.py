#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler


class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        r=''
        msg = self.get_query_argument('msg', None)
        if msg:
            r = '用户名或密码错误'
        self.render('login.html',result=r)



    def post(self, *args, **kwargs):
        pass

class LoginHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass
    def post(self, *args, **kwargs):
        ua = self.get_body_argument('username', None)
        ps = self.get_body_argument('password', None)
        if ua == 'abc' and ps =='123':
            #如果用户上传了文件，把上传的文件保存到服务器
            #self.request是RequestHandler的一个属性，引用HttpServerRequest对象
            #该对象中封装了与请求相关的所有内容
            print(self.request)
            #HttpServerRequest对象的files属性引用着用户通过表单上传的文件
            #如果用户没有上传文件，files属性是空字典{}
            #如果上传了文件
            # {'avatar:[{
            # 'filename':上传者本地图像名称}，
            # 'body': 二进制格式标表示图像内容，
            # 'content_type': 'images/jpeg',
            # {},
            # {}......]}
            print(self.request.files)
            if self.request.files:
                avs = self.request.files['avatar']
                for a in avs:
                    body = a['body']
                    writer = open('upload/%s'%a['filename'],'wb')
                    writer.write(body)
                    writer.close()
            self.redirect('/blog?username='+ua)
        else:
            #跳转回登陆界面
            self.redirect('/?msg=fail')



class BlogHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('blog.html',
                    blogs = [{
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

    def post(self,*args,**kwargs):
        pass


app = Application(handlers=[('/',IndexHandler),
                            ('/login',LoginHandler),
                            ('/blog',BlogHandler)],
                  template_path = 'mytemplate',
                  static_path = 'mystatics')


define('duankou',type=int,default = 8888)

parse_config_file('../config/config')

server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
