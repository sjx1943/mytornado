# xianyu/MVC/models/friendship.py
from sqlalchemy import Column, Integer, UniqueConstraint
from base.base import Base, engine

class Friendship(Base):
    __tablename__ = 'friendships'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    friend_id = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id

    def __repr__(self):
        return f"<Friendship(id={self.id}, user_id={self.user_id}, friend_id={self.friend_id})>"




# Base.metadata.create_all(engine)