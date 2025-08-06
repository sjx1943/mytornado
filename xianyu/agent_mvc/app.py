import sys
import os
import configparser
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import logging_config

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tornado.ioloop
from tornado.web import Application, RequestHandler, UIModule, StaticFileHandler
# from controllers.search_controller import AIQueryHandler
from controllers.main_controller import MainHandler, MyStaticFileHandler
# from controllers.message_details_controller import MessageDetailsHandler
from controllers.auth_controller import LoginHandler, RegisterHandler, ForgotPasswordHandler, ResetPasswordHandler, Loginmodule, Registmodule, Forgotmodule
from controllers.product_controller import ProductUploadHandler, HomePageHandler, ProductDetailHandler, ProductListHandler, ElseHomePageHandler
from controllers.chat_controller import ChatWebSocketHandler, InitiateChatHandler, ChatHandler, MessageAPIHandler, SendMessageAPIHandler, MarkMessagesReadHandler, DeleteMessagesHandler, UnreadCountHandler
from controllers.friend_profile_controller import FriendProfileHandler, DeleteFriendHandler
from controllers.search_controller import SearchHandler
from controllers.comment_controller import CommentHandler, ProductRatingHandler
from controllers.order_controller import OrderHandler, CreateOrderHandler
from motor import motor_tornado
import redis
from models.friendship import Friendship
from models.user import User

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "mystatics"),
    'template_path': os.path.join(os.path.dirname(__file__), "templates"),
    'upload_path': os.path.join(os.path.dirname(__file__), "mystatics/images"),
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    "login_url": "/login",
    'cookie_secret': 'sjxxxx',
    'xsrf_cookies': True
}

def make_app():
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    # 获取 MongoDB 连接信息
    mongo_host = config.get('mongodb', 'host')
    mongo_port = config.getint('mongodb', 'port')
    mongo_db = config.get('mongodb', 'database')

    mongo = motor_tornado.MotorClient(f'mongodb://{mongo_host}:{mongo_port}')[mongo_db]

    redis_client = redis.StrictRedis()

    return Application([
        (r"/", MainHandler),
        (r"/main", MainHandler),
        (r"/home_page", HomePageHandler),
        (r"/else_home_page", ElseHomePageHandler),

        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/forgot_password", ForgotPasswordHandler),
        (r"/reset_password", ResetPasswordHandler),
        (r"/product/upload", ProductUploadHandler, dict(app_settings=settings)),
        (r"/product_list", ProductListHandler),
        (r"/product/detail/([0-9]+)", ProductDetailHandler),
        
        # 评价相关路由
        (r"/api/comments", CommentHandler),
        (r"/api/comments/([0-9]+)", CommentHandler),
        (r"/api/product/([0-9]+)/rating", ProductRatingHandler),
        
        # 订单相关路由
        (r"/orders", OrderHandler),
        (r"/orders/([0-9]+)", OrderHandler),
        (r"/create_order", CreateOrderHandler),
        
        # 聊天和消息相关路由
        (r"/api/messages", MessageAPIHandler, dict(mongo=mongo)),
        (r"/api/search", SearchHandler),
        (r"/api/send_message", SendMessageAPIHandler, dict(mongo=mongo)),
        (r"/chat_room", ChatHandler, dict(mongo=mongo)),
        (r"/ws/chat_room", ChatWebSocketHandler, dict(mongo=mongo)),
        (r"/initiate_chat", InitiateChatHandler, dict(mongo=mongo)),
        (r"/friend_profile", FriendProfileHandler, dict(mongo=mongo)),
        (r"/delete_friend", DeleteFriendHandler,dict(mongo=mongo)),
        (r"/api/delete_messages", DeleteMessagesHandler, dict(mongo=mongo)),
        (r"/api/mark_messages_read", MarkMessagesReadHandler, dict(mongo=mongo)),
        (r"/api/unread_count", UnreadCountHandler, dict(mongo=mongo)),
        (r"/static/(.*)", MyStaticFileHandler, {"path": settings['static_path']}),
    ],
        ui_modules={'loginmodule': Loginmodule,
                    'registmodule': Registmodule,
                    'forgotmodule': Forgotmodule
                    }, debug = True,
        **settings
    )


if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Tornado Application')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    
    app = make_app()
    app.listen(args.port)
    print(f"后端已在端口 {args.port} 启动")
    tornado.ioloop.IOLoop.current().start()