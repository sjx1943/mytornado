#coding=utf-8
import json

from tornado.web import RequestHandler,Application
from tornado.websocket import WebSocketHandler
from MVC.models.product import Product
from sqlalchemy.orm import Session
from tornado.ioloop import IOLoop
import os
import datetime

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('chat.html')

userList = set()

class ChatHandler(WebSocketHandler):
    connections = {}  # 用于存储用户和WebSocket连接的映射
    def initialize(self):
        self.session = Session()

    def open(self, *args, **kwargs):
        print("WebSocket opened")
        user_id = self.get_secure_cookie("user_id")  # 获取当前登录的用户ID
        self.connections[user_id] = self  # 将当前连接添加到映射中

    def on_message(self, message):
        message = json.loads(message)
        if message['type'] == 'want':
            # Find the seller's WebSocket connection and send a message
            seller_id = Product.find_seller_by_product_id(message['productId'], self.session)
            seller_connection = self.connections.get(seller_id)
            if seller_connection:
                seller_connection.write_message(
                    u'%s wants your product %s' % (message['userId'], message['productId'])
                )
    def on_close(self):
        print("WebSocket closed")
        user_id = self.get_secure_cookie("user_id")  # Get the current logged in user's ID
        del self.connections[user_id]  # Remove the connection from the dictionary

# app = Application([
#     (r'^/()$', IndexHandler),
#     (r'^/chat/?$', ChatHandler),
#     (r'^/websocket/?$', ChatHandler),
# ],template_path=os.path.join(os.getcwd(),'templates'),debug=True)
#
# app.listen(8000,address='192.168.9.81')
#
# IOLoop.instance().start()