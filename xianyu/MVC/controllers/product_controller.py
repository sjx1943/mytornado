import tornado.web
import os
from sqlalchemy.orm import Session
from models.product import Product, ProductImage
from sqlalchemy.orm import sessionmaker, scoped_session
from base.base import engine
from models.user import User
import json
import re

Session = sessionmaker(bind=engine)

class ProductDetailHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def get(self, product_id):

        product = self.session.query(Product).filter_by(id=product_id).first()
        uploader = self.session.query(User).filter_by(id=product.user_id).first()
        user = self.get_current_user()

        if user:
            user_id = user.id
        else:
            user_id = None

        self.render('product_detail.html', product=product, uploader=uploader, user_id=user_id, product_id=product_id)

class ProductUploadHandler(tornado.web.RequestHandler):
    def initialize(self, app_settings):
        self.app_settings = app_settings
        self.session = Session()

    def get(self):
        # 获取指定product_id的产品信息

        self.render("publish_product.html")

    #上传商品...
    def post(self):
        # Retrieve product data from the request
        name = self.get_argument("name")
        description = self.get_argument("description")
        price = float(self.get_argument("price"))
        quantity = int(self.get_argument("quantity"))
        tag = self.get_argument("tag")  # Get the tag from the form
        images = self.request.files.get("images", [])

        if not images:
            self.set_status(400)
            self.write({"error": "Missing 'image' argument"})
            return

        # Retrieve the user_id from the current logged-in user
        user_id = self.get_secure_cookie("user_id")
        if user_id is None:
            self.set_status(400)
            self.write({'error': 'User not logged in'})
            return

        # Validate product data
        if self.validate_product_data(name, description, price, images, quantity):
            # Create a new product without image
            new_product = Product(
                name=name,
                description=description,
                price=price,
                user_id=user_id,
                tag=tag,  # Use the tag from the form
                image="",  # Temporarily set image as an empty string
                quantity=quantity,
                status="在售"
            )
            self.session.add(new_product)
            self.session.commit()

            # Save images and update the product image field
            for image in images:
                filename = image["filename"]
                filepath = os.path.join(self.app_settings["static_path"], "images", filename)
                with open(filepath, "wb") as f:
                    f.write(image["body"])
                new_product.image = filename
                self.session.add(new_product)
                self.session.commit()

            self.write(json.dumps({'product_id': new_product.id}))
        else:
            self.set_status(400)
            self.write({'error': 'Invalid product data'})

        self.redirect("/home_page")

    def validate_product_data(self, name, description, price, images, quantity):
            # 验证产品数据是否合法
        if name and description and price > 0 and len(images) > 0 and quantity >0:
            return True
        else:
            return False

    def on_finish(self):
        self.session.close()


class ProductListHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        tags= self.get_arguments("tag")  # 获取多个tag参数
        if tags:
            products = self.session.query(Product).filter(Product.tag.in_(tags)).all()
        else:
            products = self.session.query(Product).all()

        products_list = [
            {
                'id': product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "tag": product.tag,
                "image": product.image,
                "quantity": product.quantity,
                "user_id": product.user_id
            }
            for product in products
        ]
        self.write(json.dumps(products_list))


    def on_finish(self):
        self.session.remove()


class HomePageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            user_id = user_id.decode('utf-8')
            user = self.session.query(User).filter_by(id=user_id).first()
            products_list = self.session.query(Product).filter_by(user_id=user_id).all()

            # 修改这行，添加 user_id 参数
            self.render("home_page.html", products=products_list, username=user.username, user_id=user_id)
        else:
            self.redirect("/login")

    def on_finish(self):
        self.session.remove()

class ElseHomePageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get(self):
        user_id = self.get_argument("user_id", None)
        if user_id is None:
            self.write("User ID is required")
            return

        try:
            user_id = int(user_id)
            user = self.session.query(User).filter_by(id=user_id).first()
            if not user:
                self.write("User not found")
                return

            # 获取当前登录用户对象
            current_user = None
            current_user_id = self.get_secure_cookie("user_id")
            if current_user_id:
                current_user = self.session.query(User).filter_by(id=int(current_user_id)).first()

            products = self.session.query(Product).filter_by(user_id=user_id).all()

            self.render("else_home_page.html",
                        products=products,
                        username=user.username,
                        user_id=user_id,
                        current_user=current_user  # 直接传递User对象或None
                        )

        except ValueError:
            self.write("Invalid User ID format")
        except Exception as e:
            self.write(f"Error: {str(e)}")
        finally:
            self.session.remove()