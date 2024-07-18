#coding=utf-8

from tornado.web import RequestHandler,Application
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
import os
import datetime

class ChatHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat.html')

userList = set()

class EchoWebSocket(WebSocketHandler):

    def open(self, *args, **kwargs):
        print("WebSocket connection opened")
        userList.add(self)
        [user.write_message(u'%s-%s:上线了~'%(self.request.remote_ip,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def on_message(self, message):
        print("Received message: " + message)
        [user.write_message(u'%s-%s说:%s' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),message)) for user in userList]

    def on_close(self):
        userList.remove(self)
        [user.write_message(
            u'%s-%s:下线了~' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def check_origin(self, origin: str) -> bool:
        return True

    def on_pong(self, data: bytes) -> None:
        print('pong')
        super().on_pong(data)

app = Application([
    (r'^/$',ChatHandler),
    (r'^/chat$',EchoWebSocket),
],static_path=os.path.join(os.path.dirname(__file__), "mystatics"),template_path=os.path.join(os.getcwd(),'mytemplate'),debug=True)

# app.listen(9000,address='192.168.9.165')
app.listen(9000)

IOLoop.instance().start()