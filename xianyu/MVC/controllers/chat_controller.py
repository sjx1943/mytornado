#coding=utf-8
import json

from tornado.web import RequestHandler,Application
from tornado.websocket import WebSocketHandler
from MVC.models.product import Product
from sqlalchemy.orm import scoped_session, sessionmaker
from MVC.base.base import engine
import os
import datetime

Session = sessionmaker(bind=engine)

class ChatHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat.html')


class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    @staticmethod
    def find_user_by_id(user_id):
        # 这里模拟从数据库获取用户信息的过程
        # 实际应用中应该从数据库中查询用户信息
        return User(user_id, "Username" + str(user_id))

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
# app = Application([
#     (r'^/()$', IndexHandler),
#     (r'^/chat/?$', ChatHandler),
#     (r'^/websocket/?$', ChatHandler),
# ],template_path=os.path.join(os.getcwd(),'templates'),debug=True)
#
# app.listen(8000,address='192.168.9.81')
#
# IOLoop.instance().start()