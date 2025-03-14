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
from bson.objectid import ObjectId

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
        self.user_id = int(user_id)  # Ensure user_id is an integer
        connections[self.user_id] = self
        logging.warning(f"WebSocket connection established, user_id: {self.user_id}")
        self.send_stored_messages()

    @coroutine
    def send_stored_messages(self):
        try:
            user_id = self.user_id
            product_id = self.get_argument("product_id")
            if not user_id or not product_id:
                return
            messages = yield self.mongo.chat_messages.find({
                "to_user_id": user_id,
                "product_id": int(product_id),
                "status": "unread"
            }).to_list(length=None)
            logging.info(f"Found {len(messages)} unread messages for user_id: {user_id} and product_id: {product_id}")
            for message in messages:
                message['_id'] = str(message['_id'])

                # 强制格式化时间戳
                if 'timestamp' in message:
                    if isinstance(message['timestamp'], datetime.datetime):
                        message['timestamp'] = message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    else:  # 如果是字符串，尝试解析并格式化
                        try:
                            message['timestamp'] = datetime.datetime.fromisoformat(message['timestamp']).strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # 如果解析失败，记录错误并使用原始值或提供默认值
                            logging.error(f"Invalid timestamp format: {message['timestamp']}")
                            message['timestamp'] = "Invalid Date"  # 或者使用一个默认值

                from_user_id = message['from_user_id']
                to_user_id = message['to_user_id']
                # Fetch usernames if not present
                if 'from_username' not in message:
                    from_user = yield self.mongo.users.find_one({"_id": from_user_id})
                    message['from_username'] = from_user['username'] if from_user else '未知发件人'
                if 'to_username' not in message:
                    to_user = yield self.mongo.users.find_one({"_id": to_user_id})
                    message['to_username'] = to_user['username'] if to_user else '未知收件人'
                if self.ws_connection:
                    self.write_message(json.dumps(message))
                    # 更新消息状态为已读
                    yield self.mongo.chat_messages.update_one(
                        {"_id": ObjectId(message['_id'])},  # 使用 ObjectId
                        {"$set": {"status": "read"}}
                    )
                else:
                    break
            if self.ws_connection:  # Check if WebSocket connection is open
                self.write_message(
                    json.dumps({"info": f"Offline messages pushed successfully, total: {len(messages)}"}))
        except Exception as e:
            logging.error(f"Error sending stored messages: {e}")
            if self.ws_connection:  # Check if WebSocket connection is open
                self.write_message(json.dumps({"error": str(e)}))

    @coroutine
    def on_message(self, message):
        try:
            data = json.loads(message)
            target_user_id = int(data.get("target_user_id"))
            from_user_id = int(self.get_secure_cookie("user_id").decode('utf-8'))
            from_username = self.get_secure_cookie("username").decode('utf-8')
            message_content = data.get("message")
            product_id = int(data.get("product_id"))
            product_name = data.get("product_name")

            if not all([target_user_id, message_content, product_id, product_name]):
                self.write_message(json.dumps({"error": "Missing required parameters"}))
                return
            target_user = yield self.mongo.users.find_one({"_id": target_user_id})
            to_username = target_user['username'] if target_user else '没有找到用户'

            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            # Insert message into MongoDB
            yield self.mongo.chat_messages.insert_one({
                "from_user_id": from_user_id,
                "from_username": from_username,
                "to_user_id": target_user_id,
                "to_username": to_username,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": timestamp,
                "status": "unread"
            })

            message_data = {
                "from_user_id": from_user_id,
                "from_username": from_username,
                "to_user_id": target_user_id,
                "to_username": to_username,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": timestamp
            }

            if target_user_id in connections:
                connections[target_user_id].write_message(json.dumps(message_data))
            else:
                logging.info(f"User {target_user_id} is not connected, message stored in database")

        except json.JSONDecodeError:
            self.write_message(json.dumps({"error": "Invalid message format."}))
        except Exception as e:
            self.write_message(json.dumps({"error": str(e)}))


class ChatHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    @coroutine
    def get(self):
        user_id = self.get_secure_cookie("user_id")
        username = self.get_secure_cookie("username")
        product_id = self.get_argument("product_id", None)
        if product_id is None:
            product_id =0
        else:
            product_id = int(product_id)
        product_obj = self.session.query(Product).filter_by(id=product_id).first()
        product_name = product_obj.name if product_obj else "Unknown Product"

        if user_id is not None:
            user_id = int(user_id.decode('utf-8'))
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
                "id": friend.id,
                "username": friend.username
            })

        unread_messages = self.session.query(ChatMessage).filter(
            ChatMessage.receiver_id == user_id,
            ChatMessage.status == "unread"
        ).all()

        user_products = self.session.query(Product).filter_by(user_id=user_id).all()
        product_links = [{"product_id": product.id, "product_name": product.name} for product in user_products]

        # Fetch all messages for the chat room
        all_messages = yield self.mongo.chat_messages.find({
            "$or": [{"from_user_id": user_id}, {"to_user_id": user_id}],
            "product_id": int(product_id)
        }).sort("timestamp", 1).to_list(length=None)

        # Ensure all messages have from_username and to_username
        for message in all_messages:
            message['_id'] = str(message['_id'])

            # 强制格式化时间戳
            if 'timestamp' in message:
                if isinstance(message['timestamp'], datetime.datetime):
                    message['timestamp'] = message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                else:  # 如果是字符串，尝试解析并格式化
                    try:
                        message['timestamp'] = datetime.datetime.fromisoformat(message['timestamp']).strftime(
                            "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        # 如果解析失败，记录错误并使用原始值或提供默认值
                        logging.error(f"Invalid timestamp format: {message['timestamp']}")
                        message['timestamp'] = "Invalid Date"  # 或者使用一个默认值
            if 'from_username' not in message:
                from_user = yield self.mongo.users.find_one({"_id": message['from_user_id']})
                message['from_username'] = from_user['username'] if from_user else 'Unknown'
            if 'to_username' not in message:
                to_user = yield self.mongo.users.find_one({"_id": message['to_user_id']})
                message['to_username'] = to_user['username'] if to_user else 'Unknown'

        # Remove duplicate messages
        unique_messages = {msg['_id']: msg for msg in all_messages}.values()
        broadcasts = []
        recent_products = self.session.query(Product).order_by(Product.id.desc()).limit(10).all()
        for product in recent_products:
            uploader = self.session.query(User).filter_by(id=product.user_id).first()
            broadcasts.append({
                "product_id": product.id,
                "product_name": product.name,
                "uploader": uploader.username if uploader else "Unknown",
                "time": product.upload_time.strftime("%Y-%m-%d %H:%M:%S") if product.upload_time else "",
                "image": "/mystatics/images/c.png"
            })

            # Render the template with broadcasts
        self.render(
            'chat_room.html',
            current_user=username,
            friends=friends,
            broadcasts=broadcasts,
            unread_messages=unread_messages,
            product_name=product_name,
            user_id=user_id,
            all_messages=unique_messages,
            product_links=product_links,
            length=len  # Add the length filter to the context
        )


class InitiateChatHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    @coroutine
    def get(self):
        user_id = self.get_argument("user_id")
        product_id = self.get_argument("product_id")
        # Your logic to initiate chat
        self.redirect(f"/chat_room?user_id={user_id}&product_id={product_id}")

    # @coroutine
    # def post(self):
    #     user_id = self.get_secure_cookie("user_id")
    #     target_user_id = self.get_argument("target_user_id")
    #     product_id = self.get_argument("product_id")
    #     product_name = self.get_argument("product_name")
    #
    #     if not all([user_id, target_user_id, product_id, product_name]):
    #         self.write({"error": "Missing required parameters"})
    #         return
    #
    #     # Insert initial chat message or chat initiation logic here
    #     self.write({"status": "Chat initiated successfully"})