from typing import Optional, Awaitable
from MVC.models.product import Product
from sqlalchemy.orm import sessionmaker, scoped_session
from MVC.base.base import engine
import tornado
from MVC.models.user import User
import urllib.parse
import tornado.web

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        absolute_path = urllib.parse.unquote(absolute_path)
        return super().validate_absolute_path(root, absolute_path)


Session = sessionmaker(bind=engine)



class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()

    # def get_current_user(self):
    #     return self.get_secure_cookie("user")
    #     # 获取用户信息、推荐商品等...

    def get_current_user(self):
        username = self.get_secure_cookie("user")
        if username is not None:
            user = self.session.query(User).filter_by(
                username=username.decode()).first()  # Query the user from the database using the username
            return user
        return None
    def prepare(self):
        if not self.current_user:
            self.redirect("/login")
            return

    def get_products(self):
        # 获取商品列表...
        products = self.session.query(Product).all()
        self.session.close()

        products_list = [
            {
                'id': product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "tag": product.tag,
                "image": product.image
            }
            for product in products
        ]
        return products_list

    def get(self):
        user = self.current_user
        username = user.username if user else None
        products = self.get_products()
        tags = [product['tag'] for product in products]
        # self.write("已经成功登陆"+username)

        self.render("main_page.html", username=username, \
                    products = products, tags = tags)



