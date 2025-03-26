# python
# File: xianyu/MVC/controllers/friend_profile_controller.py
from itertools import product

import tornado.web
from sqlalchemy.orm import scoped_session, sessionmaker
from models.user import User
from models.product import Product
from models.friendship import Friendship
from base.base import engine

Session = sessionmaker(bind=engine)

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
            # Retrieve user_id from secure cookie and pass it to the template.
            products = self.session.query(Product).filter(Product.user_id == friend.id).all()
            user_id_cookie = self.get_secure_cookie("user_id")
            user_id = int(user_id_cookie.decode("utf-8")) if user_id_cookie else None
            self.render("friend_profile.html", friend=friend, products=products, user_id=user_id)
        else:
            self.write("Friend not found")

class DeleteFriendHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        friend_id_arg = self.get_argument("friend_id", None)
        user_id = int(self.get_secure_cookie("user_id").decode("utf-8"))
        if friend_id_arg:
            try:
                friend_id = int(friend_id_arg)
            except ValueError:
                self.write("Invalid friend id")
                return
            friendship = self.session.query(Friendship).filter_by(user_id=user_id, friend_id=friend_id).first()
            if friendship:
                self.session.delete(friendship)
                self.session.commit()
            else:
                self.write("Friendship record not found")
                return
        self.redirect("/chat_room")