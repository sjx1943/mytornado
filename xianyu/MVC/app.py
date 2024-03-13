import tornado.ioloop
import tornado.web
from controllers.main_controller import MainHandler
from controllers.auth_controller import LoginHandler, RegisterHandler, ForgotPasswordHandler, \
    ResetPasswordHandler, Loginmodule, Registmodule, Forgotmodule
# from controllers.product_controller import ProductListHandler, ProductDetailHandler,
# from controllers.chat_controller import ChatHandler


from views import *

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/main", MainHandler),
        (r"/login", LoginHandler),
        (r"/regist", RegisterHandler),
        (r"/forgot", ForgotPasswordHandler),
        (r"/reset", ResetPasswordHandler),
        # (r"/product", ProductListHandler),
        # (r"/product/detail", ProductDetailHandler),
        # (r"/chat", ChatHandler),
        # 静态文件路径配置
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ],template_path = "templates",
        ui_modules={'loginmodule':Loginmodule,'registmodule': Registmodule, 'forgotmodule': Forgotmodule},
        cookie_secret='sjxxx',xsrf_cookies=True)

# settings={
#     'handlers':[
#         (r'^/login/$',LoginHandler),
#         (r'^/center/$',CenterHandler)
#     ],'template_path':os.path.join(os.getcwd(),'templates')
# }

#cookie_secret 对应键值的作用是加密cookie中的数据，默认为随机键值加密，安全考虑用固定键值
if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
