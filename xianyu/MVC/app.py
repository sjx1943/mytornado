
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
from controllers.chat_controller import ChatWebSocketHandler, InitiateChatHandler, ChatHandler, MessageDetailsHandler, MessageAPIHandler, SendMessageAPIHandler
from controllers.friend_profile_controller import FriendProfileHandler, DeleteFriendHandler
from motor import motor_tornado
import redis

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
        (r"/message_details", MessageDetailsHandler,dict(mongo=mongo)),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/forgot_password", ForgotPasswordHandler),
        (r"/reset_password", ResetPasswordHandler),
        (r"/product/upload", ProductUploadHandler, dict(app_settings=settings)),
        (r"/product_list", ProductListHandler),
        (r"/product/detail/([0-9]+)", ProductDetailHandler),
        (r"/api/messages", MessageAPIHandler, dict(mongo=mongo)),
        (r"/api/send_message", SendMessageAPIHandler, dict(mongo=mongo)),
        (r"/chat_room", ChatHandler, dict(mongo=mongo)),
        (r"/ws/chat_room", ChatWebSocketHandler, dict(mongo=mongo)),
        (r"/initiate_chat", InitiateChatHandler, dict(mongo=mongo)),
        (r"/friend_profile", FriendProfileHandler),
        (r"/delete_friend", DeleteFriendHandler),
        (r"/static/(.*)", MyStaticFileHandler, {"path": settings['static_path']}),
    ],  debug = True,
        ui_modules={'loginmodule': Loginmodule,
                    'registmodule': Registmodule,
                    'forgotmodule': Forgotmodule
                    },
        **settings
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print("后端已顺利启动啦")
    tornado.ioloop.IOLoop.current().start()