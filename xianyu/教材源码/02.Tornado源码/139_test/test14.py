#coding=utf-8
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
import os
from tornado.web import StaticFileHandler

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('loadStatic.html')

app = Application([
    (r'/index',IndexHandler),
    # (r'/static/(.*)',StaticFileHandler,{'path':os.path.join(os.getcwd(),'static')}),
],template_path=os.path.join(os.getcwd(),'templates'),xsrf_cookies=True,static_path=os.path.join(os.getcwd(),'static'))

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()
