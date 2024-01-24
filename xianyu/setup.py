import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define
from tornado.options import options
from tornado.websocket import WebSocketHandler


class BaseHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument('name', '未传入姓名', True)  # 获取前端参数name,未传就是"未传入姓名",去除前后空格
        response = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Title</title>
</head>
<body>
<h1>我是一级标题</h1>
<h2>您好！{}!</h2>
</body>
</html>""".format(name)
        self.write(response)  # 返回给前端


if __name__ == '__main__':
    define('port', default=8080, help='设置启动服务的端口', type=int)  # 定义端口, 可以全局使用options.port获取,可通过命令行更改
    options.parse_command_line()  # 分析命令行参数
    application = tornado.web.Application(handlers=[('/', BaseHandler)])  # 设置路由
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)  # 监听端口8080,可以通过命令行改变,python xxx.py --port=8090
    tornado.ioloop.IOLoop.instance().start()  # 启动web服务