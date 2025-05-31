
import sys
import os
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
    mongo = motor_tornado.MotorClient('mongodb://localhost:27017').chat_app
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
    app = make_app()
    app.listen(8000)
    print("后端已顺利启动啦")
    tornado.ioloop.IOLoop.current().start()