# 产品建表
from sqlalchemy import create_engine, desc, Column, text, ForeignKey,and_
from sqlalchemy.orm import declarative_base, sessionmaker,joinedload
from sqlalchemy.types import Integer, String, DateTime, Float
from sqlalchemy.sql import func
from MVC.base.base import Base, engine

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)
    tag = Column(String(255))
    image = Column(String(255))

    def __init__(self, name, description, price, user_id, tag, image):
        self.name = name
        self.description = description
        self.price = price
        self.user_id = user_id
        self.tag = tag
        self.image = image

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, user_id={self.user_id}, tag={self.tag})>"


# Base.metadata.create_all(engine)
