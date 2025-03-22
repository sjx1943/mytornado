from itertools import product
from typing import Optional, Awaitable
from models.product import Product
from sqlalchemy.orm import sessionmaker, scoped_session
from base.base import engine
import tornado
from models.user import User
import urllib.parse
import tornado.web
import logging
class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        absolute_path = urllib.parse.unquote(absolute_path)
        return super().validate_absolute_path(root, absolute_path)


Session = sessionmaker(bind=engine)

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        # self.session = Session()
        self.session = scoped_session(Session)

    # def get_current_user(self):
    #     return self.get_secure_cookie("user")
    #     # 获取用户信息、推荐商品等...

    def get_current_user(self):
        try:
            username = self.get_secure_cookie("username")
            if username:
                user = self.session.query(User).filter_by(username=username.decode()).first()
                return user
        except Exception as e:
            logging.error(f"Error fetching current user: {e}")
        return None

    def prepare(self):
        if not self.current_user:
            self.redirect("/login")
            raise tornado.web.Finish()

    def get_products(self):
        # 获取商品列表...
        products = self.session.query(Product).all()
        # self.session.close()

        products_list = [
            {
                'id': product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "quantity": product.quantity,
                "tag": product.tag,
                "status": product.status,
                "image": product.image,
                "user_id": str(product.user_id)
            }
            for product in products
        ]
        return products_list

    def get(self):
        user_id = self.get_secure_cookie("user_id")
        username = self.get_secure_cookie("username")
        products = self.get_products()
        tags = [product['tag'] for product in products]
        if user_id is not None:
            user_id = user_id.decode('utf-8')
        if username is not None:
            username = username.decode('utf-8')

        product_id = products[0]['id'] if products else None
        # print('products打印显示:')
        # for product in products:
        #     print(product)

        self.render("main_page.html", username=username, user_id=user_id, tags=tags, products=products,
                    product_id=product_id)

    def on_finish(self) -> None:
        self.session.remove()