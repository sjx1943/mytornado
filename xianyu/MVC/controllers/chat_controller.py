#coding=utf-8

from tornado.web import RequestHandler,Application
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
import os
import datetime

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat.html')

userList = set()

class ChatHandler(WebSocketHandler):
    # 处理WebSocket连接、消息和关闭...


    def open(self, *args, **kwargs):

        userList.add(self)
        [user.write_message(u'%s-%s:上线了~'%(self.request.remote_ip,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def on_message(self, message):
        [user.write_message(u'%s-%s说:%s' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),message)) for user in userList]

    def on_close(self):
        userList.remove(self)
        [user.write_message(
            u'%s-%s:下线了~' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def check_origin(self, origin):
        return True  # 允许来自任何origin的WebSocket连接

app = Application([
    (r'^/()$', IndexHandler),
    (r'^/chat/?$', ChatHandler),
    (r'^/websocket/?$', ChatHandler),
],template_path=os.path.join(os.getcwd(),'templates'),debug=True)

app.listen(8000,address='192.168.9.81')

IOLoop.instance().start()