#coding=utf-8


from base import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from user import User
from product import Product


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('xu_user.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    content = Column(String(500))

    user = relationship('User', back_populates='comments')
    product = relationship('Product', back_populates='comments')

# Base.metadata.create_all(engine)
