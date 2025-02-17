# app.py
import sys
import os

# Import logging configuration
import logging_config

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import tornado.ioloop
from tornado.web import Application, RequestHandler, UIModule, StaticFileHandler
from controllers.main_controller import MainHandler, MyStaticFileHandler
from controllers.auth_controller import LoginHandler, RegisterHandler, ForgotPasswordHandler, ResetPasswordHandler, Loginmodule, Registmodule, Forgotmodule
from controllers.product_controller import ProductUploadHandler, HomePageHandler, ProductDetailHandler, ProductListHandler
from controllers.chat_controller import ChatWebSocketHandler, InitiateChatHandler, ChatHandler
from motor import motor_tornado
import redis

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "mystatics"),
    'template_path': os.path.join(os.path.dirname(__file__), "templates"),
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
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/forgot_password", ForgotPasswordHandler),
        (r"/reset_password", ResetPasswordHandler),
        (r"/product/upload", ProductUploadHandler),
        (r"/product/list", ProductListHandler),
        (r"/product/detail/([0-9]+)", ProductDetailHandler),
        (r"/chat_room", ChatHandler, dict(mongo=mongo)),
        (r"/ws/chat_room", ChatWebSocketHandler, dict(mongo=mongo)),
        (r"/initiate_chat", InitiateChatHandler, dict(mongo=mongo)),
        (r"/static/(.*)", MyStaticFileHandler, {"path": settings['static_path']}),
    ],
        ui_modules={'loginmodule': Loginmodule,
                    'registmodule': Registmodule,
                    'forgotmodule': Forgotmodule
                    },
        **settings
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

    