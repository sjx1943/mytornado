import tornado.web
import os
from sqlalchemy.orm import Session
from MVC.models.product import Product
from sqlalchemy.orm import sessionmaker, scoped_session
from MVC.base.base import engine
import json

class ProductListHandler(tornado.web.RequestHandler):
    def get(self):
        pass

        # 获取商品列表...


class ProductUploadHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session(engine)

    def get(self):
        # 获取指定product_id的产品信息

        self.render("publish_product.html")

    #上传商品...
    def post(self):
        # 从请求中获取产品数据
        name = self.get_argument("name")
        description = self.get_argument("description")
        price = float(self.get_argument("price"))
        images = self.request.files.get("images", [])
        user_id = 1  # 假设当前登录用户的ID为1

        # 验证产品数据
        if self.validate_product_data(name, description, price, images):
            # 创建新的产品
            new_product = Product(
                name=name,
                description=description,
                price=price,
                user_id=user_id,
                tag="生活用品"
            )
            self.session.add(new_product)

            # 保存产品图片
            for image in images:
                filename = f"{new_product.id}_{image.filename}"
                new_image = ProductImage(
                    filename=filename,
                    product_id=new_product.id
                )
                self.session.add(new_image)
                with open(os.path.join("static", "images", filename), "wb") as f:
                    f.write(image.body)

            self.session.commit()
            self.write(json.dumps({'product_id': new_product.id}))
        else:
            self.set_status(400)
            self.write(json.dumps({'error': 'Invalid product data'}))

    def validate_product_data(self, name, description, price, images):
            # 验证产品数据是否合法
        if name and description and price > 0 and len(images) > 0:
            return True
        else:
            return False

    def on_finish(self):
        self.session.close()


#设计商品发布相关控制器，路由关联为/publish_product