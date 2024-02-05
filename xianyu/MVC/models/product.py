import sqlalchemy
from sqlalchemy import create_engine, desc, Column, text, ForeignKey,and_
from sqlalchemy.orm import declarative_base, sessionmaker,joinedload
from sqlalchemy.types import Integer, String, DateTime, Float
from sqlalchemy.sql import func

conn_url = 'mysql+pymysql://sgg:Zpepc001@localhost:3306/xianyu_db?charset=utf8mb4'
engine = create_engine(conn_url, echo=True, pool_recycle=3600)
Base = declarative_base()
#Base.metadata.create_all(engine)
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    user_id = Column(Integer, nullable=False)

    def __init__(self, id, name, description, price, user_id):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.user_id = user_id

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price}, user_id={self.user_id})>"


Base.metadata.create_all(engine)
