#coding=utf-8

from tornado.web import RequestHandler,Application
from tornado.ioloop import IOLoop
import os
from tornado.websocket import WebSocketHandler



class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class SocketHandler(WebSocketHandler):
    def open(self, *args, **kwargs):
        print u'建立服务器连接'

    def on_message(self, message):
        print u'收到客户端的消息:%s'%message
        self.write_message('hello client!')


    def on_close(self):
        print u'断开服务器连接'

    def check_origin(self, origin):
        return True

if __name__ == '__main__':



    app = Application([
        (r'^/$',IndexHandler),
        (r'^/websocket/$',SocketHandler),
    ],template_path=os.path.join(os.getcwd(),'templates'))

    app.listen(8000)

    IOLoop.instance().start()