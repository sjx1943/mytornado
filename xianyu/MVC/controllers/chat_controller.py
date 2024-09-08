# chat_controller.py
import tornado.web
import tornado.websocket
import json
from models.product import Product
from models.chat import Chat
from models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker
from base.base import engine
user_sessions = {}

Session = scoped_session(sessionmaker(bind=engine))

class ChatHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)  # Initialize session

    def on_finish(self):
        self.session.close()  # Close session

    def get(self):
        user_id = self.get_secure_cookie("user_id")
        username = self.get_secure_cookie("username")

        if user_id is not None:
            user_id = user_id.decode('utf-8')
        if username is not None:
            username = username.decode('utf-8')

        # Retrieve recent messages from the Chat model
        recent_messages = self.session.query(Chat).filter(
            (Chat.user1_id == user_id) | (Chat.user2_id == user_id)
        ).order_by(Chat.id.desc()).limit(10).all()

        friends = []
        for message in recent_messages:
            friend_id = message.user2_id if message.user1_id == user_id else message.user1_id
            friend = self.session.query(User).filter_by(id=friend_id).first()
            friends.append({
                'username': friend.username,
                'message': message.message
            })

        # Retrieve recent product uploads for system broadcast
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

        self.render('chat_room.html', current_user=username, friends=friends, broadcasts=broadcasts)

class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.user_id = self.get_argument("user_id")
        self.product_id = self.get_argument("product_id", None)
        self.session = scoped_session(Session)  # Initialize session

        if self.product_id:
            product = self.session.query(Product).filter(Product.id == self.product_id).first()
            if product is None:
                raise ValueError(f"No product found with id {self.product_id}")
            self.partner_id = product.user_id
            self.channel_id = f"{self.user_id}_{self.partner_id}" if int(
                self.user_id) < self.partner_id else f"{self.partner_id}_{self.user_id}"
        else:
            self.channel_id = 'public'

        if self.channel_id not in user_sessions:
            user_sessions[self.channel_id] = set()
        user_sessions[self.channel_id].add(self)

        self.write_message(f"Welcome to the chat room: {self.channel_id}")

    def on_message(self, message):
        try:
            message_data = json.loads(message)
            chat_message = Chat(user1_id=self.user_id, user2_id=self.partner_id, message=message_data['content'])
            self.session.add(chat_message)
            self.session.commit()
            for user in user_sessions[self.channel_id]:
                user.write_message(f"{self.user_id} says: {message_data['content']}")
        except json.JSONDecodeError:
            self.write_message("Error: Invalid JSON format")

    def on_close(self):
        user_sessions[self.channel_id].remove(self)
        if not user_sessions[self.channel_id]:
            del user_sessions[self.channel_id]
        self.session.close()  # Close session

    def check_origin(self, origin: str) -> bool:
        return True