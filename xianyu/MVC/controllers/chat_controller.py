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

class PublicChatHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('public_chat.html')

class PrivateChatHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('private_chat.html')

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
user_sessions = {}

# PublicChatWebSocket class
class PublicChatWebSocket(WebSocketHandler):
    def open(self, *args, **kwargs):
        print("WebSocket connection opened")
        userList.add(self)
        [user.write_message(u'%s-%s:上线了~' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def on_message(self, message):
        print("Received message: " + message)
        [user.write_message(u'%s-%s说:%s' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)) for user in userList]

    def on_close(self):
        userList.remove(self)
        [user.write_message(u'%s-%s:下线了~' % (self.request.remote_ip, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))) for user in userList]

    def check_origin(self, origin: str) -> bool:
        return True

# PrivateChatWebSocket class
class PrivateChatWebSocket(WebSocketHandler):
    def open(self, *args, **kwargs):
        self.user_id = self.get_argument("user_id")
        self.partner_id = self.get_argument("partner_id", None)  # Default to None if not provided
        if not self.partner_id:
            self.write_message("Error: Missing partner_id")
            self.close()
            return

        self.channel_id = f"{self.user_id}_{self.partner_id}" if self.user_id < self.partner_id else f"{self.partner_id}_{self.user_id}"

        if self.channel_id not in user_sessions:
            user_sessions[self.channel_id] = set()
        user_sessions[self.channel_id].add(self)

        self.write_message(f"xxx 对你的商品感兴趣啊！: {self.channel_id}")

    def on_message(self, message):
        message_data = json.loads(message)
        for user in user_sessions[self.channel_id]:
            user.write_message(f"{self.user_id} says: {message_data['content']}")

    def on_close(self):
        user_sessions[self.channel_id].remove(self)
        if not user_sessions[self.channel_id]:
            del user_sessions[self.channel_id]

    def check_origin(self, origin: str) -> bool:
        return True

# app = Application([
#     (r'^/()$', IndexHandler),
#     (r'^/chat/?$', ChatHandler),
#     (r'^/websocket/?$', ChatHandler),
# ],template_path=os.path.join(os.getcwd(),'templates'),debug=True)
#
# app.listen(8000,address='192.168.9.81')
#
# IOLoop.instance().start()