# chat.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, desc, Column, text, ForeignKey, and_, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, joinedload, relationship
from sqlalchemy.types import Integer, String, DateTime, Float
from sqlalchemy.sql import func
# from user import User
from base.base import Base, engine
# from product import Product

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product_name = Column(String(255))  # 新增字段
    message = Column(String(255), nullable=False)
    status = Column(String(64), default="unread")
    timestamp = Column(DateTime, server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, message={self.message})>"



# Base.metadata.create_all(engine)





