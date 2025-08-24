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


class BlockFriendHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    def post(self):
        try:
            data = json.loads(self.request.body)
            friend_id = int(data.get("friend_id"))
            user_id_cookie = self.get_secure_cookie("user_id")
            if not user_id_cookie:
                self.write({"success": False, "message": "请先登录"})
                return
            
            user_id = int(user_id_cookie.decode("utf-8"))
            
            # 查找好友关系
            friendship = self.session.query(Friendship).filter(
                ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
                ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
            ).first()

            if not friendship:
                self.write({"success": False, "message": "好友关系不存在"})
                return

            # 更新状态
            if friendship.status == 'active':
                friendship.status = 'blocked'
                message = '好友已拉黑'
            else:
                friendship.status = 'active'
                message = '已取消拉黑'
            
            self.session.commit()
            self.write({"success": True, "message": message})

        except Exception as e:
            self.session.rollback()
            self.write({"success": False, "message": str(e)})
        finally:
            self.session.remove()


class InitiateChatHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo
        self.session = scoped_session(Session)

    def get(self):
        try:
            seller_id = int(self.get_argument("user_id"))
            buyer_id_cookie = self.get_secure_cookie("user_id")
            if not buyer_id_cookie:
                self.redirect("/login")
                return
            
            buyer_id = int(buyer_id_cookie.decode("utf-8"))

            if seller_id == buyer_id:
                # 如果是自己的商品，可以重定向到首页或提示信息
                self.redirect("/main")
                return

            # 检查是否被拉黑
            friendship = self.session.query(Friendship).filter(
                ((Friendship.user_id == buyer_id) & (Friendship.friend_id == seller_id)) |
                ((Friendship.user_id == seller_id) & (Friendship.friend_id == buyer_id))
            ).first()

            if friendship and friendship.status == 'blocked':
                self.write("您已被对方拉黑，无法添加好友")
                return

            # 检查是否已经是好友 (A -> B)
            existing_friendship_ab = self.session.query(Friendship).filter(
                (Friendship.user_id == buyer_id) &
                (Friendship.friend_id == seller_id)
            ).first()

            if not existing_friendship_ab:
                new_friendship_ab = Friendship(user_id=buyer_id, friend_id=seller_id)
                self.session.add(new_friendship_ab)

            # 检查是否已经是好友 (B -> A)
            existing_friendship_ba = self.session.query(Friendship).filter(
                (Friendship.user_id == seller_id) &
                (Friendship.friend_id == buyer_id)
            ).first()

            if not existing_friendship_ba:
                new_friendship_ba = Friendship(user_id=seller_id, friend_id=buyer_id)
                self.session.add(new_friendship_ba)
            
            self.session.commit()

            # 重定向到聊天室，并带上好友ID以便自动打开聊天窗口
            self.redirect(f"/chat_room?friend_id={seller_id}")

        except Exception as e:
            self.session.rollback()
            self.write(f"发生错误: {e}")
        finally:
            self.session.remove()


class FriendProfileHandler(tornado.web.RequestHandler):
    def initialize(self, mongo):
        self.mongo = mongo  # 确保这里正确接收了mongo连接
        self.session = scoped_session(Session)

    async def post(self):
        try:
            data = json.loads(self.request.body)
            friend_id = int(data.get("friend_id"))
            user_id = int(data.get("user_id"))  # 从请求体中获取user_id

            # 检查是否已经是好友
            existing_friendship = self.session.query(Friendship).filter(
                (Friendship.user_id == user_id) &
                (Friendship.friend_id == friend_id)
            ).first()

            if existing_friendship:
                self.write({"success": False, "message": "已经是好友"})
                return

            # 创建新的好友关系
            new_friendship = Friendship(
                user_id=user_id,
                friend_id=friend_id
            )
            self.session.add(new_friendship)
            self.session.commit()

            self.write({"success": True, "message": "好友添加成功"})
        except Exception as e:
            self.session.rollback()
            self.write({"success": False, "message": str(e)})
        finally:
            self.session.remove()

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