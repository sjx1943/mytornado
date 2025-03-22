#coding=utf-8

from tornado.ioloop import IOLoop
from tornado.web import Application
from urls import *

class HttpServer(Application):
    def __init__(self,port=8000):
        self.listen(port)
        Application.__init__(self,**settings)

    def start(self):
        IOLoop.instance().start()


if __name__ == '__main__':
    HttpServer().start()