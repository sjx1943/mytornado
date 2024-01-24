#coding=utf-8
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application

class SetCookieHandler(RequestHandler):
    def get(self, *args, **kwargs):
        #普通设置方式
        # self.set_cookie('uname','zhangsan',expires_days=3)
        #加密设置方式
        self.set_secure_cookie('uname','lisi',expires_days=3)


class GetCookieHandler(RequestHandler):
    def get(self, *args, **kwargs):
        # 普通取值方式
        # self.write(self.get_cookie('uname'))
        # 加密取值方式
        self.write(self.get_secure_cookie('uname'))

settings = {'cookie_secret':'fdafdsa'}

app = Application([
    (r'/set',SetCookieHandler),
    (r'/get',GetCookieHandler)
],**settings)


if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()