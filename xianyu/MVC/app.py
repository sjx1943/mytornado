import sys
import os

# Add the directory containing the MVC module to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tornado.ioloop
import os
from tornado.web import Application, RequestHandler, UIModule, StaticFileHandler
from controllers.main_controller import MainHandler, MyStaticFileHandler
from controllers.auth_controller import LoginHandler, RegisterHandler, ForgotPasswordHandler, \
    ResetPasswordHandler, Loginmodule, Registmodule, Forgotmodule
from controllers.product_controller import ProductUploadHandler, HomePageHandler, ProductDetailHandler
from controllers.chat_controller import ChatHandler, ChatWebSocket
# from controllers.product_controller import ProductListHandler, ProductDetailHandler,
# from controllers.chat_controller import ChatHandler


from views import *

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "mystatics"),
    'template_path': os.path.join(os.path.dirname(__file__), "templates"),
    "login_url": "/login",
    'cookie_secret': 'sjxxx',
    'xsrf_cookies': True
}

def make_app():
    return Application([
        (r"/", MainHandler),
        (r"/main", MainHandler),
        (r"/login", LoginHandler),
        (r"/regist", RegisterHandler),
        (r"/forgot", ForgotPasswordHandler),
        (r"/reset", ResetPasswordHandler),
        (r"/publish_product",ProductUploadHandler, dict(app_settings=settings)),
        (r"/home_page", HomePageHandler),
        (r"/product/detail/([0-9]+)", ProductDetailHandler),
        (r'^/chat_room$', ChatHandler),
        (r"/chat$", ChatWebSocket),
        # 静态文件路径配置
        (r"/mystatics/(.*)", MyStaticFileHandler, {"path": settings["static_path"]}),
    ],
        ui_modules={'loginmodule':Loginmodule,
                    'registmodule': Registmodule,
                    'forgotmodule': Forgotmodule
                    },
        **settings
    )

#cookie_secret 对应键值的作用是加密cookie中的数据，默认为随机键值加密，安全考虑用固定键值
if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
