#coding=utf-8
import json

from tornado.web import RequestHandler,Application
from tornado.websocket import WebSocketHandler
from MVC.models.product import Product
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from tornado.ioloop import IOLoop
import os
import datetime


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat.html')

userList = set()

class User:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    @staticmethod
    def find_user_by_id(user_id):
        # 这里模拟从数据库获取用户信息的过程
        # 实际应用中应该从数据库中查询用户信息
        return User(user_id, "Username" + str(user_id))

class ChatHandler(WebSocketHandler):
    connections = {}  # 存储用户ID到WebSocket连接的映射

    def open(self):
        user_id = self.get_secure_cookie("user_id").decode('utf-8')
        if user_id:
            self.connections[user_id] = self
            print(f"WebSocket opened for user {user_id}")

    def on_message(self, message):
        # 解析消息
        self.write_message(u"You said: " + message)
        message_dict = json.loads(message)
        sender_id = message_dict.get('sender_id')
        receiver_id = message_dict.get('receiver_id')
        text = message_dict.get('text')

        # 确保发送者和接收者都有效
        if sender_id in self.connections and receiver_id in self.connections:
            # 向接收者发送消息
            receiver_conn = self.connections[receiver_id]
            receiver_conn.write_message(f"From {sender_id}: {text}")

    def on_close(self):
        user_id = self.get_secure_cookie("user_id").decode('utf-8')
        if user_id in self.connections:
            del self.connections[user_id]
            print(f"WebSocket closed for user {user_id}")

# app = Application([
#     (r'^/()$', IndexHandler),
#     (r'^/chat/?$', ChatHandler),
#     (r'^/websocket/?$', ChatHandler),
# ],template_path=os.path.join(os.getcwd(),'templates'),debug=True)
#
# app.listen(8000,address='192.168.9.81')
#
# IOLoop.instance().start()