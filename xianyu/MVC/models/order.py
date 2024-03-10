#coding=utf-8


from MVC.base.base import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from user import User
from product import Product


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('xu_user.id'))
    quantity = Column(Integer)
    status = Column(String(50))

    product = relationship('Product', back_populates='orders')
    user = relationship('User', back_populates='orders')

# Base.metadata.create_all(engine)
