import tornado.web
import os
from sqlalchemy.orm import Session
from MVC.models.product import Product, ProductImage
from sqlalchemy.orm import sessionmaker, scoped_session
from MVC.base.base import engine
from MVC.models.user import User
import json
import re


class ProductListHandler(tornado.web.RequestHandler):
    def get(self):
        pass

        # 获取商品列表...


class ProductUploadHandler(tornado.web.RequestHandler):
    def initialize(self, app_settings):
        self.app_settings = app_settings
        # self.settings = settings
        self.session = Session(engine)

    def get(self):
        # 获取指定product_id的产品信息

        self.render("publish_product.html")

    #上传商品...
    def post(self):
        # Retrieve product data from the request
        name = self.get_argument("name")
        description = self.get_argument("description")
        price = float(self.get_argument("price"))
        images = self.request.files.get("images", [])
        # images = self.get_argument('images', None)
        if not images:
            self.set_status(400)
            self.write({"error": "Missing 'image' argument"})
            return

        # Retrieve the user_id from the current logged-in user
        user_id = self.get_secure_cookie("user_id")
        # Replace this with your method of retrieving the logged-in user's ID
        if user_id is None:
            self.set_status(400)
            self.write({'error': 'User not logged in'})
            return

        # Validate product data
        if self.validate_product_data(name, description, price, images):
            # Create a new product without image
            new_product = Product(
                name=name,
                description=description,
                price=price,
                user_id=user_id,
                tag="生活用品",
                image=""  # Temporarily set image as an empty string
            )
            self.session.add(new_product)
            self.session.commit()  # Commit here to get the new_product.id

            # Save product images
            for image in images:
                # Remove non-ASCII characters from the filename
                filename = re.sub(r'[^\x00-\x7F]+', '', image['filename'])
                filename = f"{new_product.id}_{filename}"
                new_image = ProductImage(
                    filename=filename,
                    product_id=new_product.id
                )
                self.session.add(new_image)
                with open(os.path.join(self.app_settings['static_path'], "images", filename), "wb") as f:
                    f.write(image['body'])

            # Update the product image
            new_product.image = filename  # Use the filename with the id_ prefix
            self.session.commit()

            self.write(json.dumps({'product_id': new_product.id}))
        else:
            self.set_status(400)
            self.write(json.dumps({'error': 'Invalid product data'}))
        self.redirect("/home_page")

    def validate_product_data(self, name, description, price, images):
            # 验证产品数据是否合法
        if name and description and price > 0 and len(images) > 0:
            return True
        else:
            return False

    def on_finish(self):
        self.session.close()


#设计商品发布相关控制器，路由关联为/publish_product

class HomePageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session(engine)

    def get_current_user(self):
        username = self.get_secure_cookie("user")
        if username is not None:
            user = self.session.query(User).filter_by(
                username=username.decode()).first()  # Query the user from the database using the username
            return user
        return None

    def get(self):
        user = self.current_user
        if user is None:
            self.redirect("/login")
            return

        # Retrieve the latest products uploaded by the current user
        products = self.session.query(Product).filter_by(user_id=user.id).order_by(Product.id.desc()).all()
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

        self.render("home_page.html", products=products_list)