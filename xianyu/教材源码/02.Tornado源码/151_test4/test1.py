#coding=utf-8

from tornado.web import RequestHandler,Application
import os
from tornado.ioloop import IOLoop
# class IndexHandler(RequestHandler):
#     @asynchronous
#     def get(self,filename):
#         print(filename)
#         BaseDir = os.path.join(os.getcwd(),'static',filename)
#         with open(BaseDir,'rb') as fr:
#             content = fr.read()
#
#         if not content:
#             self.write_error(404)
#         else:
#             self.set_header('Content-Type','image/png')
#             self.write(content)
#
#
#         #手动结束此次响应
#         self.finish()
#

class IndexHandler(RequestHandler):
    def get(self, filename):
        print(filename)
        BaseDir = os.path.join(os.getcwd(), 'static', filename)
        with open(BaseDir, 'rb') as fr:
            content = fr.read()

        if not content:
            self.write_error(404)
        else:
            self.set_header('Content-Type', 'image/png')
            self.write(content)

        # Manually end this response
        self.finish()




app = Application([
    (r'^/static/(.*)$',IndexHandler)
])


app.listen(8000)


IOLoop.instance().start()

