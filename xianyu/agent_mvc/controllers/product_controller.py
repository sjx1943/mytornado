import tornado.web
import os
from sqlalchemy.orm import Session
from models.product import Product, ProductImage
from sqlalchemy.orm import sessionmaker, scoped_session
from base.base import engine
from models.user import User
import json
import re
from models.comment import Comment
from models.order import Order

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
        
        if not product or product.status == '已删除':
            self.set_status(404)
            self.write("商品不存在或已被删除")
            return
            
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
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            self.redirect("/login")
            return
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
        tags = self.get_arguments("tag")
        query = self.session.query(Product).filter(
            Product.status == '在售',
            Product.quantity > 0
        )
        if tags and 'all' not in tags:
            query = query.filter(Product.tag.in_(tags))
        
        products = query.all()

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
            
            # 获取用户的所有商品
            all_products = self.session.query(Product).filter(
                Product.user_id == user_id
            ).order_by(Product.upload_time.desc()).all()

            self.render("home_page.html", 
                        products=all_products, 
                        username=user.username, 
                        user_id=user_id)
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

            # 获取当前登录用户ID
            current_user_id_val = None
            current_user_cookie = self.get_secure_cookie("user_id")
            if current_user_cookie:
                current_user_id_val = int(current_user_cookie)

            products = self.session.query(Product).filter_by(user_id=user_id).all()

            self.render("else_home_page.html",
                        products=products,
                        username=user.username,
                        user_id=user_id,
                        current_user_id=current_user_id_val
                        )

        except ValueError:
            self.write("Invalid User ID format")
        except Exception as e:
            self.write(f"Error: {str(e)}")
        finally:
            self.session.remove()


class UpdateProductStatusHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = scoped_session(Session)

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def post(self, product_id):
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            product = self.session.query(Product).filter_by(id=product_id).first()
            if not product:
                self.write(json.dumps({'success': False, 'error': '商品不存在'}))
                return

            if product.user_id != user.id:
                self.write(json.dumps({'success': False, 'error': '您没有权限修改此商品'}))
                return

            data = json.loads(self.request.body)
            new_status = data.get("status")
            new_quantity = data.get("quantity")

            if new_status not in ["在售", "已下架"]:
                self.write(json.dumps({'success': False, 'error': '无效的商品状态'}))
                return

            # 如果是重新上架，必须确保数量大于0
            if new_status == "在售":
                if new_quantity is None:
                    # 如果前端没有传递数量，就检查现有数量
                    if product.quantity <= 0:
                        self.write(json.dumps({'success': False, 'error': '商品数量为0，请先更新数量再上架'}))
                        return
                elif int(new_quantity) <= 0:
                    self.write(json.dumps({'success': False, 'error': '上架失败，商品数量必须大于0'}))
                    return
                else:
                    product.quantity = int(new_quantity)

            product.status = new_status
            self.session.commit()
            self.write(json.dumps({'success': True, 'message': '商品状态更新成功'}))

        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))
        finally:
            self.session.remove()


class DeleteProductHandler(tornado.web.RequestHandler):
    """软删除商品处理器"""
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def post(self, product_id):
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            product = self.session.query(Product).filter_by(id=product_id, user_id=user.id).first()
            if not product:
                self.write(json.dumps({'success': False, 'error': '商品不存在或无权限'}))
                return

            product.status = '已删除'
            self.session.commit()
            self.write(json.dumps({'success': True, 'message': '商品已删除'}))

        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))
        finally:
            self.session.close()

class PhysicalDeleteProductHandler(tornado.web.RequestHandler):
    """
    物理删除商品处理器（高风险操作）
    """
    def initialize(self, app_settings):
        self.app_settings = app_settings
        self.session = Session()

    def get_current_user(self):
        # 在实际应用中，这里应该增加管理员权限校验
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def post(self, product_id):
        try:
            user = self.get_current_user()
            if not user: # 应该添加管理员验证
                self.write(json.dumps({'success': False, 'error': '权限不足'}))
                return

            product = self.session.query(Product).filter_by(id=product_id).first()
            if not product:
                self.write(json.dumps({'success': False, 'error': '商品不存在'}))
                return

            # 1. 检查是否存在不可删除的关联数据（如订单）
            order_exists = self.session.query(Order).filter_by(product_id=product.id).first()
            if order_exists:
                self.write(json.dumps({
                    'success': False,
                    'error': '无法删除，因为该商品存在关联的订单记录。请先将商品状态设为“已删除”。'
                }))
                return

            # 2. 删除可删除的关联数据
            self.session.query(Comment).filter_by(product_id=product.id).delete()
            
            # 3. 删除图片文件
            if product.image:
                image_path = os.path.join(self.app_settings["upload_path"], product.image)
                if os.path.exists(image_path):
                    os.remove(image_path)

            # 4. 删除商品本身
            self.session.delete(product)
            
            self.session.commit()
            self.write(json.dumps({'success': True, 'message': '商品已从数据库中永久删除'}))

        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': f'操作失败: {str(e)}'}))
        finally:
            self.session.close()

class AdminDashboardHandler(tornado.web.RequestHandler):
    """管理员仪表盘处理器"""
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        # 在实际应用中，这里应该增加管理员权限校验
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def get(self):
        user = self.get_current_user()
        if not user: # 应该添加管理员验证
            self.redirect("/login")
            return
        
        deleted_products = self.session.query(Product).filter_by(status='已删除').all()
        self.render("admin_dashboard.html", products=deleted_products)

    def on_finish(self):
        self.session.close()