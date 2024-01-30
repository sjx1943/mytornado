import tornado.ioloop
import tornado.web
from controllers.main_controller import MainHandler
from controllers.auth_controller import LoginHandler, RegisterHandler
from controllers.product_controller import ProductHandler, ProductDetailHandler
from controllers.chat_controller import ChatRoomHandler
from views import *
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/product", ProductHandler),
        (r"/product/detail", ProductDetailHandler),
        (r"/chat", ChatRoomHandler),
        # 静态文件路径配置
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])

# settings={
#     'handlers':[
#         (r'^/login/$',LoginHandler),
#         (r'^/center/$',CenterHandler)
#     ],'template_path':os.path.join(os.getcwd(),'templates')
# }

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
