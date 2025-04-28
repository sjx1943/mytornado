# File: xianyu/MVC/controllers/friend_profile_controller.py
from datetime import datetime
from itertools import product
import json
import tornado.web
from sqlalchemy.orm import scoped_session, sessionmaker
from models.user import User
from models.product import Product
from models.friendship import Friendship
from base.base import engine

Session = sessionmaker(bind=engine)



class FriendProfileHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    @tornado.gen.coroutine
    def get(self):
        friend_id = self.get_argument("friend_id", None)
        user_id_cookie = self.get_secure_cookie("user_id")
        user_id = int(user_id_cookie.decode("utf-8")) if user_id_cookie else None

        if not friend_id:
            self.write("Invalid friend id")
            return

        try:
            friend_id = int(friend_id)
            friend = self.session.query(User).filter_by(id=friend_id).first()

            if not friend:
                self.write("Friend not found")
                return

            # 获取聊天消息
            messages = yield self.mongo.chat_messages.find({
                "$or": [
                    {"from_user_id": user_id, "to_user_id": friend_id},
                    {"from_user_id": friend_id, "to_user_id": user_id}
                ]
            }).sort("timestamp", 1).to_list(length=None)

            # 格式化消息
            for msg in messages:
                msg['_id'] = str(msg['_id'])
                if isinstance(msg['timestamp'], datetime.datetime):
                    msg['timestamp'] = msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")

            # 获取好友产品
            products = self.session.query(Product).filter(Product.user_id == friend.id).all()

            self.render("chat_room.html",
                        current_user=self.get_secure_cookie("username").decode("utf-8"),
                        user_id=user_id,
                        friend=friend,
                        messages=messages,
                        products=products
                        )

        except Exception as e:
            self.write(f"Error: {str(e)}")



class DeleteFriendHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    def post(self):
        try:
            # 解析请求数据
            data = json.loads(self.request.body)
            friend_id = int(data.get("friend_id"))
            user_id = int(data.get("user_id")) # 从请求体中获取 user_id
            # user_id = int(self.get_secure_cookie("user_id").decode("utf-8"))

            # 验证参数
            if not friend_id or not user_id:
                self.write({"status": "error", "error": "缺少必要参数"})
                return

            # 删除好友关系
            self.session.query(Friendship).filter(
                (Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)
            ).delete(synchronize_session=False)

            # 同步删除MongoDB中的消息
            self.mongo.chat_messages.delete_many({
                "$or": [
                    {"from_user_id": user_id, "to_user_id": friend_id},
                    {"from_user_id": friend_id, "to_user_id": user_id}
                ]
            })

            self.session.commit()
            self.write({"status": "success"})

        except Exception as e:
            self.session.rollback()
            self.write({"status": "error", "error": str(e)})

        finally:
            self.session.remove()