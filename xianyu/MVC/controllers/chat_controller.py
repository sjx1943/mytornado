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
import logging

Session = sessionmaker(bind=engine)
connections = {}

class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    def open(self):
        user_id = self.get_argument("user_id", None)
        if user_id is None or not user_id.isdigit():
            logging.warning("WebSocket connection opened with invalid user_id, connection closed.")
            self.close()
            return
        self.user_id = str(user_id)  # Ensure user_id is a string
        connections[self.user_id] = self
        logging.info(f"WebSocket connection established, user_id: {self.user_id}")
        self.send_stored_messages()

    @coroutine
    def send_stored_messages(self):
        try:
            user_id = self.user_id
            if not user_id:
                return

            messages = yield self.mongo.chat_messages.find({"to_user_id": user_id, "status": "unread"}).to_list(length=None)
            logging.info(f"Found {len(messages)} unread messages for user_id: {user_id}")

            for message in messages:
                message['_id'] = str(message['_id'])  # Convert ObjectId to string
                if 'timestamp' in message:
                    message['timestamp'] = message['timestamp'].isoformat()  # Convert datetime to string
                if self.ws_connection:  # Check if WebSocket connection is open
                    self.write_message(json.dumps(message))
                else:
                    break

            if self.ws_connection:  # Check if WebSocket connection is open
                self.write_message(json.dumps({"info": f"Offline messages pushed successfully, total: {len(messages)}"}))

        except Exception as e:
            logging.error(f"Error sending stored messages: {e}")
            if self.ws_connection:  # Check if WebSocket connection is open
                self.write_message(json.dumps({"error": str(e)}))

    @coroutine
    def on_message(self, message):
        try:
            data = json.loads(message)
            target_user_id = str(data.get("target_user_id"))
            message_content = data.get("message")
            product_id = str(data.get("product_id"))
            product_name = data.get("product_name")

            if not all([target_user_id, message_content, product_id, product_name]):
                self.write_message(json.dumps({"error": "Missing required parameters"}))
                return

            # Insert message into MongoDB
            yield self.mongo.chat_messages.insert_one({
                "from_user_id": self.user_id,
                "to_user_id": target_user_id,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "status": "unread"
            })

            message_data = {
                "from_user_id": self.user_id,
                "to_user_id": target_user_id,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

            if target_user_id in connections:
                connections[target_user_id].write_message(json.dumps(message_data))
            else:
                logging.info(f"User {target_user_id} is not connected, message stored in database")

        except json.JSONDecodeError:
            self.write_message(json.dumps({"error": "Invalid message format."}))
        except Exception as e:
            self.write_message(json.dumps({"error": str(e)}))

    def on_close(self):
        if self.user_id in connections:
            del connections[self.user_id]
            logging.info(f"WebSocket connection closed, user_id: {self.user_id}")

    def check_origin(self, origin):
        return True

class ChatHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    @coroutine
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
                "id": str(friend.id),
                "username": friend.username
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
                "product_id": str(product.id),
                "product_name": product.name,
                "uploader": uploader.username,
                "time": product.upload_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Fetch the product name based on the product_id
        product_name = None
        if product_id:
            product = self.session.query(Product).filter_by(id=product_id).first()
            if product:
                product_name = product.name

        self.render('chat_room.html', current_user=username, friends=friends, broadcasts=broadcasts, unread_messages=unread_messages, product_name=product_name, user_id=user_id)
        # Call send_stored_messages from ChatWebSocketHandler
        ws_handler = ChatWebSocketHandler(self.application, self.request, mongo=self.mongo)
        ws_handler.user_id = str(user_id)
        yield ws_handler.send_stored_messages()

    def on_finish(self):
        self.session.remove()

class InitiateChatHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    @coroutine
    def post(self):
        user_id = self.get_secure_cookie("user_id")
        target_user_id = self.get_argument("target_user_id")
        product_id = self.get_argument("product_id")
        product_name = self.get_argument("product_name")

        if not all([user_id, target_user_id, product_id, product_name]):
            self.write({"error": "Missing required parameters"})
            return

        # Insert initial chat message or chat initiation logic here
        self.write({"status": "Chat initiated successfully"})