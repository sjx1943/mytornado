#coding=utf-8
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.web import RedirectHandler

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        #方式1：
        # self.set_status(302)
        # self.set_header('Location','https://www.baidu.com')

        #方式2：
        self.redirect('https://www.jd.com')

app = Application([
    (r'/index',IndexHandler),
    (r'/index2',RedirectHandler,{'url':'https://www.taobao.com'}),
])

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()