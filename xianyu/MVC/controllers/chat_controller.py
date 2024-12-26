# chat_controller.py

import tornado.web
import tornado.websocket
import json
from models.product import Product
from models.chat import ChatMessage
from models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker
from base.base import engine
from tornado.gen import coroutine
from motor import motor_tornado
import redis
import datetime
from tornado.websocket import WebSocketHandler

Session = sessionmaker(bind=engine)
connections = {}

class ChatWebSocketHandler(WebSocketHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    def open(self):
        self.user_id = self.get_argument("user_id", None)
        self.product_id = self.get_argument("product_id", None)

        if self.user_id:
            connections[self.user_id] = self
            print(f"WebSocket opened for user_id: {self.user_id}")

    @coroutine
    def on_message(self, message):
        try:
            data = json.loads(message)
            target_user_id = data.get("target_user_id")
            message_content = data.get("message")
            product_id = data.get("product_id")
            product_name = data.get("product_name")

            if not all([target_user_id, message_content, product_id, product_name]):
                self.write_message(json.dumps({"error": "Missing message fields."}))
                return

            # Insert message into MongoDB
            yield self.mongo.chat_messages.insert_one({
                "from_user_id": self.user_id,
                "to_user_id": target_user_id,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": datetime.datetime.utcnow()
            })

            if target_user_id in connections:
                connections[target_user_id].write_message(json.dumps({
                    "from_user_id": self.user_id,
                    "message": message_content,
                    "product_id": product_id,
                    "product_name": product_name
                }))
            else:
                self.write_message(json.dumps({
                    "error": "Target user is not online."
                }))
        except json.JSONDecodeError:
            self.write_message(json.dumps({"error": "Invalid message format."}))
        except Exception as e:
            self.write_message(json.dumps({"error": str(e)}))

    def on_close(self):
        if self.user_id in connections:
            del connections[self.user_id]
            print(f"WebSocket closed for user_id: {self.user_id}")

    def check_origin(self, origin):
        return True

class ChatHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def on_finish(self):
        self.session.close()

    def get(self):
        user_id = self.get_secure_cookie("user_id")
        username = self.get_secure_cookie("username")
        product_id = self.get_argument("product_id", None)

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

        # Fetch the product name based on the product_id
        product_name = None
        if product_id:
            product = self.session.query(Product).filter_by(id=product_id).first()
            if product:
                product_name = product.name

        self.render('chat_room.html', current_user=username, friends=friends, broadcasts=broadcasts, unread_messages=unread_messages, product_name=product_name, user_id=user_id)

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