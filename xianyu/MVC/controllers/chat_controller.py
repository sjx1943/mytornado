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
        if user_id is None:
            logging.warning("WebSocket connection opened without user_id, connection closed.")
            self.close()
            return
        self.user_id = int(user_id)  # Ensure user_id is an integer
        connections[self.user_id] = self
        logging.info(f"WebSocket connection established, user_id: {self.user_id}")
        self.send_stored_messages()

    @coroutine
    def send_stored_messages(self):
        try:
            user_id = self.user_id
            if not user_id:
                logging.error("User ID is not set")
                return

            messages = yield self.mongo.chat_messages.find({"to_user_id": user_id, "status": "unread"}).to_list(length=None)
            for message in messages:
                sender = yield self.mongo.users.find_one({"id": message["from_user_id"]})
                if sender:
                    message_data = {
                        "from_user_id": message["from_user_id"],
                        "from_username": sender["username"],
                        "message": message["message"],
                        "timestamp": message["timestamp"]
                    }
                    self.write_message(json.dumps(message_data))
                    # Mark the message as read
                    yield self.mongo.chat_messages.update_one({"_id": message["_id"]}, {"$set": {"status": "read"}})
        except Exception as e:
            logging.error(f"Error sending stored messages: {e}")

    @coroutine
    def on_message(self, message):
        try:
            data = json.loads(message)
            target_user_id = str(data.get("target_user_id"))  # Ensure target_user_id is a string
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
                "status": "unread",
                "timestamp": datetime.datetime.utcnow()
            })

            message_data = {
                "from_user_id": self.user_id,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

            if int(target_user_id) in connections:
                connections[int(target_user_id)].write_message(json.dumps(message_data))
            else:
                logging.warning(f"Receiver user_id: {target_user_id} is not connected.")
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

    def on_finish(self):
        self.session.remove()

class InitiateChatHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        uploader_id = self.get_argument("user_id")
        # print("上传者ID: ",uploader_id)
        product_id = self.get_argument("product_id")
        current_user_id = self.get_secure_cookie("user_id")
        if current_user_id:
            current_user_id = current_user_id.decode('utf-8')
        else:
            self.redirect("/login")
            return
        product = self.session.query(Product).filter_by(id=product_id).first()

        new_message = ChatMessage(
            sender_id=current_user_id,
            receiver_id=uploader_id,
            product_id=product_id,
            product_name=product.name,
            message=f"I am interested in your product: {product.name}. Let's chat!",
            status="unread"
        )
        self.session.add(new_message)
        self.session.commit()

        self.redirect(f"/chat_room?user_id={current_user_id}&product_id={product_id}")

    def on_finish(self):
        self.session.remove()