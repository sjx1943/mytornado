# chat_controller.py
import tornado.web
import tornado.websocket
import json
from models.product import Product
from models.chat import ChatMessage
from models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker
from base.base import engine
user_sessions = {}

Session = sessionmaker(bind=engine)

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

        # Retrieve recent messages from the ChatMessage model
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

            # Retrieve unread messages for the current user
        unread_messages = self.session.query(ChatMessage).filter(
       ChatMessage.receiver_id == user_id,
                ChatMessage.status == "unread"
            ).all()

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

        # Create a new chat message to notify the product uploader
        new_message = ChatMessage(
            sender_id=current_user_id,
            receiver_id=user_id,
            product_id=product_id,
            message="I am interested in your product.",
            status="unread"
        )
        self.session.add(new_message)
        self.session.commit()

        # Redirect to the chat room
        self.redirect(f"/chat_room?user_id={user_id}&product_id={product_id}")

    def on_finish(self):
        self.session.remove()

class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def open(self):
        self.user_id = self.get_secure_cookie("user_id")
        if not self.user_id:
            self.close()
            return
        self.user_id = int(self.user_id)
        self.product_id = int(self.get_argument("product_id"))
        self.connections[self.user_id] = self

    def on_message(self, message):
        # Handle incoming messages
        chat_message = ChatMessage(
            sender_id=self.user_id,
            receiver_id=self.get_argument("user_id"),
            product_id=self.product_id,
            message=message,
            status="unread"
        )
        self.session.add(chat_message)
        self.session.commit()

        # Send the message to the receiver if they are connected
        receiver_id = int(self.get_argument("user_id"))
        if receiver_id in self.connections:
            self.connections[receiver_id].write_message(message)

    def on_close(self):
        if self.user_id in self.connections:
            del self.connections[self.user_id]

    def on_finish(self):
        self.session.remove()