#coding=utf-8

from product import Product
from user import User
from chat import Chat
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine

# Update the connection URL to use PyMySQL (`+pymysql`)

conn_url = 'mysql+pymysql://sgg:Zpepc001@localhost:3306/xianyu_db?charset=utf8mb4'
engine = create_engine(conn_url, echo=True, pool_recycle=3600)
Base = declarative_base()

#Base.metadata.create_all(engine)


# Create a session
Session = sessionmaker(bind=engine)

session = Session()


# 添加用户
new_user = User(id=1, username='john', password='password', email='john@example.com')
session.add(new_user)
session.commit()

# 查询用户
user = session.query(User).filter_by(username='john').first()

# 添加商品
new_product = Product(name='iPhone 13 Pro Max', description='The latest and greatest iPhone', price=999.99, user_id=user.id)
session.add(new_product)
session.commit()

# 查询商品
product = session.query(Product).filter_by(name='iPhone 13 Pro Max').first()

# 添加聊天
new_chat = Chat(user1_id=user.id, user2_id=2, message='Hello!')
session.add(new_chat)
session.commit()

# 查询聊天
chat = session.query(Chat).filter_by(id=1).first()

# 关闭会话
session.close()
