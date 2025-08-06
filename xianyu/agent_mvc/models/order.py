#coding=utf-8

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.base import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)  # 买家
    seller_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)  # 卖家
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)  # 成交价格
    total_amount = Column(Float, nullable=False)  # 总金额
    status = Column(String(50), nullable=False, default='pending')  # pending, confirmed, shipped, delivered, completed, cancelled
    shipping_address = Column(Text)  # 收货地址
    contact_phone = Column(String(20))  # 联系电话
    order_note = Column(Text)  # 订单备注
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)  # 完成时间

    # 关系定义（需要在User和Product模型中添加对应的back_populates）
    # product = relationship('Product', back_populates='orders')
    # buyer = relationship('User', foreign_keys=[buyer_id], back_populates='buyer_orders')
    # seller = relationship('User', foreign_keys=[seller_id], back_populates='seller_orders')

    def __init__(self, product_id, buyer_id, seller_id, quantity, price, shipping_address=None, contact_phone=None, order_note=None):
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.quantity = quantity
        self.price = price
        self.total_amount = quantity * price
        self.shipping_address = shipping_address
        self.contact_phone = contact_phone
        self.order_note = order_note

    def calculate_total(self):
        """计算订单总金额"""
        self.total_amount = self.quantity * self.price

    def __repr__(self):
        return f"<Order(id={self.id}, product_id={self.product_id}, buyer_id={self.buyer_id}, status={self.status}, total={self.total_amount})>"

# Base.metadata.create_all(engine)
