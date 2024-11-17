# chat_controller.py
import tornado.web
import tornado.websocket
import json
from models.product import Product
from models.chat import ChatMessage
from models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker
from base.base import engine


Session = sessionmaker(bind=engine)

class ChatHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def on_finish(self):
        self.session.close()

    def get(self):
        user_id = self.get_secure_cookie("user_id")
        username = self.get_secure_cookie("username")

        if user_id is not None:
            user_id = user_id.decode('utf-8')
        if username is not None:
            username = username.decode('utf-8')

        recent_messages = self.session.query(ChatMessage).filter(
            (ChatMessage.sender_id == user_id) | (ChatMessage.receiver_id == user_id)
        ).order_by(ChatMessage.id.desc()).limit(10).all()

        friends = []
        for message in recent_messages:
            friend_id = message.receiver_id if message.sender_id == user_id else message.sender_id
            friend = self.session.query(User).filter_by(id=friend_id).first()
            friends.append({
                'username': friend.username,
                'message': message.message
            })

        unread_messages = self.session.query(ChatMessage).filter(
            ChatMessage.receiver_id == user_id,
            ChatMessage.status == "unread"
        ).all()

        recent_products = self.session.query(Product).order_by(Product.id.desc()).limit(10).all()
        broadcasts = []
        for product in recent_products:
            uploader = self.session.query(User).filter_by(id=product.user_id).first()
            broadcasts.append({
                'uploader': uploader.username,
                'time': product.upload_time,
                'product_name': product.name,
                'product_id': product.id
            })

        self.render('chat_room.html', current_user=username, friends=friends, broadcasts=broadcasts, unread_messages=unread_messages)

class InitiateChatHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        user_id = self.get_argument("user_id")
        product_id = self.get_argument("product_id")
        current_user_id = self.get_secure_cookie("user_id")

        if not current_user_id:
            self.redirect("/login")
            return
        product = self.session.query(Product).filter_by(id=product_id).first()

        new_message = ChatMessage(
            sender_id=current_user_id,
            receiver_id=user_id,
            product_id=product_id,
            product_name=product.name,
            message=f"I am interested in your product: {product.name}. Let's chat!",
            status="unread"
        )
        self.session.add(new_message)
        self.session.commit()

        self.redirect(f"/chat_room?user_id={user_id}&product_id={product_id}")

    def on_finish(self):
        self.session.remove()

class ChatWebSocket(tornado.websocket.WebSocketHandler):
    clients = set()

    def open(self):
        ChatWebSocket.clients.add(self)
        self.write_message("WebSocket connection opened")

    def on_message(self, message):
        for client in ChatWebSocket.clients:
            if client != self:
                client.write_message(message)

    def on_close(self):
        ChatWebSocket.clients.remove(self)
        self.write_message("WebSocket connection closed")

    def check_origin(self, origin):
        return True