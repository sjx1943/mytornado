#coding=utf-8
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.ioloop import IOLoop

class GetRequestInfo(RequestHandler):
    def get(self, *args, **kwargs):
        # HTTPServerRequest对象
        protocol = self.request.protocol
        method = self.request.method
        uri = self.request.uri

        ua = self.request.headers['User-Agent']


        #设置响应信息
        # self.set_status(200)
        # self.set_header('Server','HelloServer')



        # self.write('%s,%s,%s'%(protocol,method,uri))

        self.set_status(302)
        self.set_header('location','https://www.baidu.com')




app = Application([
    (r'/getReq/',GetRequestInfo)
])

app.listen(8000)

IOLoop.current().start()