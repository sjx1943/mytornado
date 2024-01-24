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

    def open(self, *args, **kwargs):

        userList.add(self)
        [user.write_message(u'%s-%s:上线了~'%(self.request.remote_ip,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def on_message(self, message):
        [user.write_message(u'%s-%s说:%s' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),message)) for user in userList]

    def on_close(self):
        userList.remove(self)
        [user.write_message(
            u'%s-%s:下线了~' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]


app = Application([
    (r'^/$',IndexHandler),
    (r'^/chat/$',ChatHandler),
],template_path=os.path.join(os.getcwd(),'templates'),debug=True)

app.listen(9000,address='127.0.0.1')

IOLoop.instance().start()