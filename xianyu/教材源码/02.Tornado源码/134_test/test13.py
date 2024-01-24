#coding=utf-8
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
import os

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('login2.html')

    def post(self, *args, **kwargs):
        self.write('hello')

app = Application([
    (r'/login',IndexHandler)
],template_path=os.path.join(os.getcwd(),'templates'),xsrf_cookies=True)

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()
