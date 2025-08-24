#coding=utf-8

import tornado.web
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, sessionmaker
from models.order import Order
from models.user import User
from models.product import Product
from base.base import engine
from sqlalchemy import desc, or_, and_
from datetime import datetime

Session = sessionmaker(bind=engine)


class OrderHandler(tornado.web.RequestHandler):
    """订单管理处理器"""
    
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def get(self, order_id=None):
        """获取订单信息"""
        try:
            user = self.get_current_user()
            if not user:
                self.redirect("/login")
                return

            if order_id:
                # 获取特定订单详情
                order = self.session.query(Order).filter_by(id=order_id).first()
                if not order:
                    self.write("订单不存在")
                    return
                
                # 检查权限（只有买家或卖家能查看）
                if order.buyer_id != user.id and order.seller_id != user.id:
                    self.write("无权限查看此订单")
                    return
                
                # 获取相关信息
                product = self.session.query(Product).filter_by(id=order.product_id).first()
                buyer = self.session.query(User).filter_by(id=order.buyer_id).first()
                seller = self.session.query(User).filter_by(id=order.seller_id).first()
                
                self.render('order_detail.html', 
                           order=order, 
                           product=product, 
                           buyer=buyer, 
                           seller=seller,
                           current_user=user)
            else:
                # 获取用户的订单列表
                order_type = self.get_argument("type", "all")  # all, buying, selling
                
                if order_type == "buying":
                    orders = self.session.query(Order).filter_by(buyer_id=user.id).order_by(desc(Order.created_at)).all()
                elif order_type == "selling":
                    orders = self.session.query(Order).filter_by(seller_id=user.id).order_by(desc(Order.created_at)).all()
                else:
                    orders = self.session.query(Order).filter(
                        or_(Order.buyer_id == user.id, Order.seller_id == user.id)
                    ).order_by(desc(Order.created_at)).all()
                
                # 获取订单相关信息
                orders_data = []
                for order in orders:
                    product = self.session.query(Product).filter_by(id=order.product_id).first()
                    buyer = self.session.query(User).filter_by(id=order.buyer_id).first()
                    seller = self.session.query(User).filter_by(id=order.seller_id).first()
                    
                    orders_data.append({
                        'order': order,
                        'product': product,
                        'buyer': buyer,
                        'seller': seller,
                        'is_buyer': order.buyer_id == user.id
                    })
                
                self.render('orders_list.html', orders=orders_data, order_type=order_type, current_user=user)
                
        except Exception as e:
            self.write(f"获取订单失败: {str(e)}")

    def post(self):
        """创建订单"""
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            product_id = int(self.get_argument("product_id"))
            quantity = int(self.get_argument("quantity", 1))
            shipping_address = self.get_argument("shipping_address", "")
            contact_phone = self.get_argument("contact_phone", "")
            order_note = self.get_argument("order_note", "")

            # 验证商品是否存在
            product = self.session.query(Product).filter_by(id=product_id).first()
            if not product:
                self.write(json.dumps({'success': False, 'error': '商品不存在'}))
                return

            # 检查库存
            if product.quantity < quantity:
                self.write(json.dumps({'success': False, 'error': '库存不足'}))
                return

            # 不能购买自己的商品
            if product.user_id == user.id:
                self.write(json.dumps({'success': False, 'error': '不能购买自己的商品'}))
                return

            # 创建订单
            new_order = Order(
                product_id=product_id,
                buyer_id=user.id,
                seller_id=product.user_id,
                quantity=quantity,
                price=product.price,
                shipping_address=shipping_address,
                contact_phone=contact_phone,
                order_note=order_note
            )
            
            self.session.add(new_order)
            
            # 更新商品库存
            product.quantity -= quantity
            if product.quantity == 0:
                product.status = "已售完"
            
            self.session.commit()
            
            self.write(json.dumps({
                'success': True, 
                'message': '订单创建成功',
                'order_id': new_order.id
            }))
            
        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def put(self, order_id):
        """更新订单状态"""
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            order = self.session.query(Order).filter_by(id=order_id).first()
            if not order:
                self.write(json.dumps({'success': False, 'error': '订单不存在'}))
                return

            # 只有卖家可以更新订单状态
            if order.seller_id != user.id:
                self.write(json.dumps({'success': False, 'error': '只有卖家可以更新订单状态'}))
                return

            new_status = self.get_argument("status")
            valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'completed', 'cancelled']
            
            if new_status not in valid_statuses:
                self.write(json.dumps({'success': False, 'error': '无效的订单状态'}))
                return

            order.status = new_status
            
            if new_status == 'completed':
                order.completed_at = datetime.now()
            
            self.session.commit()
            
            self.write(json.dumps({
                'success': True, 
                'message': '订单状态更新成功',
                'new_status': new_status
            }))
            
        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def delete(self, order_id):
        """取消订单"""
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            order = self.session.query(Order).filter_by(id=order_id).first()
            if not order:
                self.write(json.dumps({'success': False, 'error': '订单不存在'}))
                return

            # 只有买家可以取消订单，且订单状态必须是pending
            if order.buyer_id != user.id:
                self.write(json.dumps({'success': False, 'error': '只有买家可以取消订单'}))
                return
                
            if order.status != 'pending':
                self.write(json.dumps({'success': False, 'error': '只能取消待确认的订单'}))
                return

            # 恢复商品库存
            product = self.session.query(Product).filter_by(id=order.product_id).first()
            if product:
                product.quantity += order.quantity
                product.status = "在售"

            order.status = 'cancelled'
            self.session.commit()
            
            self.write(json.dumps({'success': True, 'message': '订单取消成功'}))
            
        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def on_finish(self):
        self.session.close()


class CreateOrderHandler(tornado.web.RequestHandler):
    """创建订单页面处理器"""
    
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def get(self):
        """显示创建订单页面"""
        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        product_id = self.get_argument("product_id")
        product = self.session.query(Product).filter_by(id=product_id).first()
        
        if not product:
            self.write("商品不存在")
            return
            
        if product.user_id == user.id:
            self.write("不能购买自己的商品")
            return

        self.render('create_order.html', product=product, user=user)

    def on_finish(self):
        self.session.close()


class ConfirmTransactionHandler(tornado.web.RequestHandler):
    """确认交易处理器"""

    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def post(self, order_id):
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            order = self.session.query(Order).filter_by(id=order_id).first()
            if not order:
                self.write(json.dumps({'success': False, 'error': '订单不存在'}))
                return

            # 只有买家可以确认收货
            if order.buyer_id != user.id:
                self.write(json.dumps({'success': False, 'error': '只有买家可以确认收货'}))
                return
            
            if order.status != 'shipped':
                self.write(json.dumps({'success': False, 'error': '订单状态不是已发货，无法确认收货'}))
                return

            order.status = 'completed'
            order.completed_at = datetime.now()

            # 更新商品库存
            product = self.session.query(Product).filter_by(id=order.product_id).first()
            if product:
                product.quantity -= order.quantity
                if product.quantity <= 0:
                    product.status = "已售完"

            self.session.commit()

            self.write(json.dumps({'success': True, 'message': '交易确认成功'}))

        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))
        finally:
            self.session.close()
