import sqlalchemy
from sqlalchemy import create_engine, desc, Column, text, ForeignKey,and_,Integer,String
from sqlalchemy.orm import declarative_base, sessionmaker,joinedload,relationship
from sqlalchemy.types import Integer, String, DateTime, Float
from sqlalchemy.sql import func
from user import User
from base import Base, engine



class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('xu_user.id'), nullable=False)
    message = Column(String(255), nullable=False)

    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])

    def __init__(self, id, user1_id, user2_id, message):
        self.id = id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.message = message

    def __repr__(self):
        return f"<Chat(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id}, message={self.message})>"

Base.metadata.create_all(engine)