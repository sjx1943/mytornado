#coding=utf-8
import tornado.ioloop
import tornado.web
import os

class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('templates/upload.html')

class UploadHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        #获取请求参数
        #[{'body': '\x89PNG\r\n\', 'content_type': u'image/png', 'filename': 'bd_logo1.png'}]
        img1 = self.request.files['img1']

        for img in img1:
            body = img['body']
            content_type = img['content_type']
            filename = img['filename']

        with open(os.path.join(os.getcwd(),'files',filename),'wb') as fw:
            fw.write(body)

        self.set_header('Content-Type',content_type)
        self.write(body)


#创建应用
app = tornado.web.Application([
    (r'/',IndexHandler),
    (r'/upload/',UploadHandler),
])

#绑定端口号
app.listen(8000)

#启动服务器
tornado.ioloop.IOLoop.current().start()

