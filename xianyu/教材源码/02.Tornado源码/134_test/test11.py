#coding=utf-8
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
import os
from tornado.template import Template


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        #底层1
        # with open(os.path.join(os.getcwd(),'templates','temp.html'),'rb') as fr:
        #     content = fr.read()
        #
        # t = Template(content)
        # c = t.generate(uname='zhangsan')
        # self.write(c)

        #升级1
        # self.render('templates/temp.html',uname='lisi')
        self.render('temp.html',uname='wangwu')

app = Application([
    (r'/index',IndexHandler)
],template_path=os.path.join(os.getcwd(),'templates'))

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()


