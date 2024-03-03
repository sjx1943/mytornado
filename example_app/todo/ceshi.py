#!/usr/bin/env python

# -*- coding: utf-8 -*-
from absl.logging import PythonHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, parse_config_file, options
from tornado.web import Application, RequestHandler




class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('<a href = /python>try python</a><br/>')
        self.write('<a href = /java>try java</a>')
    def post(self, *args, **kwargs):
        pass

define('duankou',type=int,default = 8888)

parse_config_file('../config/config')


class JavaHandler(RequestHandler):
    def get(self, p1=None, p2=None, *args, **kwargs):
        #利用路径变化请求不同的资源
        self.write('hello java<br>')
        if p1:
            self.write('today is : '+p1+'<br>')
        else:
            self.write('day1,day2,day3,day4')
        if p2:

            self.write('the lesson is: '+p2)
    def post(self, *args, **kwargs):
        pass


class PythonHD(RequestHandler):
    def get(self, *args, **kwargs):
        #利用参数变化请求不同的资源
        self.write('hello python')
        d = self.get_query_argument('day',None)
        s = self.get_query_argument('subject',None)
        ds = self.get_query_arguments('day')
        dss = self.get_query_arguments('subject')
        print(d,s)
        print(ds,dss)



    def post(self, *args, **kwargs):
        self.write("hellp python POST")
        d = self.get_body_argument('day',None)
        s = self.get_body_argument('subject',None)
        print(d,s)
        ds = self.get_body_arguments('day')
        ss = self.get_body_arguments('subject')
        print(ds,ss)
        dss = self.get_arguments('day')
        dsss = self.get_arguments('subject')
        print(dss, dsss)

app = Application(handlers=[('/',IndexHandler),
                            ('/java',JavaHandler),
                            ('/java/(day[0-9]+)',JavaHandler),
                            ('/java/(day[0-9]+)/([a-z0-9]+)',JavaHandler),

                            ('/python',PythonHD)])
server = HTTPServer(app)
server.listen(options.duankou)
IOLoop.current().start()
