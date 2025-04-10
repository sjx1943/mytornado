# chat_controller.py

import tornado.web
import tornado.websocket
import json
from models.product import Product

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
            from_user_id = int(self.get_secure_cookie("user_id").decode("utf-8"))
            from_username = self.get_secure_cookie("username").decode("utf-8")
            message_content = data.get("message")
            product_id = int(data.get("product_id"))
            product_name = data.get("product_name")

            if not all([target_user_id, message_content, product_id, product_name]):
                self.write_message(json.dumps({"error": "Missing required parameters"}))
                return
            china_tz = datetime.timezone(datetime.timedelta(hours=8))
            # timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = datetime.datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S")

            self.mongo.chat_messages.insert_one({
                "from_user_id": from_user_id,
                "from_username": from_username,
                "to_user_id": target_user_id,
                "to_username": "Will be looked up",
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": timestamp,
                "status": "unread"
            })

            # Construct a message payload
            message_data = {
                "from_user_id": from_user_id,
                "from_username": from_username,
                "to_user_id": target_user_id,
                "message": message_content,
                "product_id": product_id,
                "product_name": product_name,
                "timestamp": timestamp
            }

            # Send to target user if connected
            if target_user_id in connections:
                connections[target_user_id].write_message(json.dumps({
                    "from_user_id": from_user_id,
                    "message": message_content,
                    "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }))
            self.write_message(json.dumps({"status": "Message sent successfully"}))

            # Also send back to sender so they see it immediately
            if from_user_id in connections:
                connections[from_user_id].write_message(json.dumps(message_data))

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
        product_id = self.get_argument("product_id", "0")  # 默认设为"0"
        selected_friend_id = self.get_argument('friend_id', None)

        # 解码cookies
        user_id = int(user_id.decode('utf-8')) if user_id else None
        username = username.decode('utf-8') if username else None

        # 处理product_id
        try:
            product_id = int(product_id)
        except ValueError:
            product_id = 0

        # 获取product_obj和product_name
        product_obj = self.session.query(Product).filter_by(id=product_id).first()
        product_name = product_obj.name if product_obj else "所有消息"

        if not product_obj:
            # Create a proper placeholder product object
            class PlaceholderProduct:
                def __init__(self):
                    self.id = 0
                    self.name = "Unknown Product"
                    self.description = ""
                    self.price = 0
                    self.user_id = 0
                    self.tag = ""
                    self.image = ""
                    self.quantity = 0
                    self.status = ""

            product_obj = PlaceholderProduct()
        else:
            product_name = product_obj.name
        # Fetch recent messages from MongoDB
        try:
            recent_messages = yield self.mongo.chat_messages.find({
                "$or": [
                    {"from_user_id": user_id},
                    {"to_user_id": user_id}
                ]
            }).sort("timestamp", -1).limit(10).to_list(length=None)
        except Exception as e:
            logging.error(f"Error fetching recent messages: {e}")
            recent_messages = []

        # Process friends
        seen_friend_ids = set()
        friends = []
        for message in recent_messages:
            friend_id = message['to_user_id'] if message['from_user_id'] == user_id else message['from_user_id']
            if friend_id not in seen_friend_ids and friend_id!=user_id:  # 添加去重判断
                seen_friend_ids.add(friend_id)
                friend_obj = self.session.query(User).filter_by(id=friend_id).first()
                if friend_obj:
                    friends.append({
                        "id": friend_obj.id,
                        "username": friend_obj.username
                    })

        # Fetch unread messages
        unread_messages = yield self.mongo.chat_messages.find({
            "to_user_id": user_id,
            "status": "unread"
        }).to_list(length=None)

        unread_group = {}
        for msg in unread_messages:
            friend_id = msg['to_user_id'] if msg['from_user_id'] == user_id else msg['from_user_id']
            if friend_id not in unread_group:
                friend_username = None
                for friend in friends:
                    if friend["id"] == friend_id:
                        friend_username = friend["username"]
                        break
                if friend_username is None:
                    friend_obj = self.session.query(User).filter_by(id=friend_id).first()
                    friend_username = friend_obj.username if friend_obj else "Unknown"
                truncated = msg['message'] if len(msg['message']) <= 5 else msg['message'][:5] + "..."
                unread_group[friend_id] = {
                    "friend_id": friend_id,
                    "username": friend_username,
                    "summary": truncated
                }

        # Fetch user products
        user_products = self.session.query(Product).filter_by(user_id=user_id).all()
        product_links = [{"product_id": p.id, "product_name": p.name} for p in user_products]

        # Fetch all messages for the current product
        all_messages = yield self.mongo.chat_messages.find({
            "$or": [
                {"from_user_id": user_id, "product_id": product_id},
                {"to_user_id": user_id, "product_id": product_id}
            ]
        }).sort("timestamp", 1).to_list(length=None)

        for message in all_messages:
            message['_id'] = str(message['_id'])
            if 'timestamp' in message:
                if isinstance(message['timestamp'], datetime.datetime):
                    message['timestamp'] = message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    try:
                        message['timestamp'] = datetime.datetime.fromisoformat(message['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logging.error(f"Invalid timestamp format: {message['timestamp']}")
                        message['timestamp'] = "Invalid Date"
            if 'from_username' not in message:
                from_user = yield self.mongo.users.find_one({"_id": message['from_user_id']})
                message['from_username'] = from_user['username'] if from_user else "Unknown"
            if 'to_username' not in message:
                to_user = yield self.mongo.users.find_one({"_id": message['to_user_id']})
                message['to_username'] = to_user['username'] if to_user else "Unknown"

        unique_messages = {msg['_id']: msg for msg in all_messages}.values()
        broadcasts = []
        recent_products = self.session.query(Product).order_by(Product.id.desc()).limit(10).all()
        for p in recent_products:
            uploader = self.session.query(User).filter_by(id=p.user_id).first()
            broadcasts.append({
                "product_id": p.id,
                "product_name": p.name,
                "uploader": uploader.username if uploader else "Unknown",
                "time": p.upload_time.strftime("%Y-%m-%d %H:%M:%S") if p.upload_time else "",
                "image": "/mystatics/images/c.png"
            })

        self.render(
            'chat_room.html',
            current_user=username,
            friends=friends,
            selected_friend_id=selected_friend_id,
            username=username,
            broadcasts=broadcasts,
            unread_group=unread_group,
            unread_messages=unread_messages,
            product_name=product_name,
            user_id=user_id,
            all_messages=unique_messages,
            product_links=product_links,
            product=product_obj,
            length=len
        )



class SendMessageHandler(tornado.web.RequestHandler):

    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    def post(self):
        user_id = self.get_argument("user_id")
        friend_id = self.get_argument("friend_id")
        message = self.get_argument("message")

        if not all([user_id, friend_id, message]):
            self.write({"error": "Missing required parameters"})
            return

        # 插入消息到 MongoDB
        self.mongo.chat_messages.insert_one({
            "user_id": user_id,
            "friend_id": friend_id,
            "message": message,
            "timestamp": datetime.datetime.utcnow(),
            "status": "unread"
        })

        # 通知目标用户（如果在线）
        if int(friend_id) in connections:
            connections[int(friend_id)].write_message(json.dumps({
                "from_user_id": user_id,
                "message": message,
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }))

        self.write({"status": "消息发送成功！"})


class MessageDetailsHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)  # 添加session初始化

    @tornado.gen.coroutine
    def get(self):
        # 安全获取用户信息
        user_id_cookie = self.get_secure_cookie("user_id")
        username_cookie = self.get_secure_cookie("username")
        user_id = int(user_id_cookie.decode("utf-8")) if user_id_cookie else None
        username = username_cookie.decode("utf-8") if username_cookie else "未知用户"

        friend_id_param = self.get_argument("friend_id", None)
        messages = []
        selected_friend = None

        if friend_id_param:
            friend_id = int(friend_id_param)
            # 获取好友信息
            selected_friend = self.session.query(User).filter_by(id=friend_id).first()
            if not selected_friend:
                selected_friend = yield self.mongo.users.find_one({"_id": friend_id})

            # 获取聊天消息
            cursor = self.mongo.chat_messages.find({
                "$or": [
                    {"from_user_id": friend_id, "to_user_id": user_id},
                    {"from_user_id": user_id, "to_user_id": friend_id}
                ]
            }).sort("timestamp", 1)
            messages = yield cursor.to_list(length=None)

            # 处理消息格式
            for msg in messages:
                msg['_id'] = str(msg['_id'])
                if 'timestamp' in msg:
                    if isinstance(msg['timestamp'], datetime.datetime):
                        msg['timestamp'] = msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        try:
                            msg['timestamp'] = datetime.datetime.fromisoformat(msg['timestamp']).strftime(
                                "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            logging.error(f"Invalid timestamp format: {msg['timestamp']}")
                            msg['timestamp'] = "Invalid Date"

                if "from_username" not in msg:
                    from_user = yield self.mongo.users.find_one({"_id": msg['from_user_id']})
                    msg["from_username"] = from_user['username'] if from_user else "未知"

                if "to_username" not in msg:
                    to_user = yield self.mongo.users.find_one({"_id": msg['to_user_id']})
                    msg["to_username"] = to_user['username'] if to_user else "未知"

        self.render(
            'message_details.html',
            messages=messages,
            user_id=user_id,
            username=username,
            selected_friend=selected_friend,
            current_user=username
        )

class FriendProfileHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        friend_id = self.get_argument("friend_id", None)
        if friend_id is None:
            self.write("Invalid friend id")
            return
        try:
            friend_id = int(friend_id)
        except ValueError:
            self.write("Invalid friend id format")
            return

        friend = self.session.query(User).filter_by(id=friend_id).first()
        if friend:
            # Pass an empty products list if no products are available.
            self.render("friend_profile.html", friend=friend, products=[])
        else:
            self.write("Friend not found")


class MessageAPIHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    @tornado.gen.coroutine
    def get(self):
        user_id = int(self.get_secure_cookie("user_id").decode("utf-8"))
        friend_id = int(self.get_argument("friend_id"))

        messages = yield self.mongo.chat_messages.find({
            "$or": [
                {"from_user_id": user_id, "to_user_id": friend_id},
                {"from_user_id": friend_id, "to_user_id": user_id}
            ]
        }).sort("timestamp", 1).to_list(length=None)

        for msg in messages:
            msg['_id'] = str(msg['_id'])
            if isinstance(msg['timestamp'], datetime.datetime):
                msg['timestamp'] = msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

        self.write(json.dumps(messages))


class SendMessageAPIHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo

    @tornado.gen.coroutine
    def post(self):
        user_id = int(self.get_secure_cookie("user_id").decode("utf-8"))
        data = json.loads(self.request.body)

        message = {
            "from_user_id": user_id,
            "from_username": self.get_secure_cookie("username").decode("utf-8"),
            "to_user_id": int(data["friend_id"]),
            "message": data["message"],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "unread"
        }

        yield self.mongo.chat_messages.insert_one(message)
        self.write({"status": "success"})


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