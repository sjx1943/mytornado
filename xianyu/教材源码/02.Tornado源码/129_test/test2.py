#coding=utf-8


'''
1.实现登录功能
2.技能点：利用Tornado获取请求参数
'''

import tornado.ioloop
import tornado.web


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('templates/login.html')


class LoginHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        #获取请求参数(GET请求方式)
        uname = self.get_query_argument('uname')
        # pwd = self.get_query_argument('pwd')
        pwd = self.get_argument('pwd')
        favs = self.get_query_arguments('fav')



        #输出到页面显示
        self.write('%s,%s,%s'%(uname,pwd,favs))

    def post(self, *args, **kwargs):
        # 获取请求参数(POST请求方式)
        uname = self.get_body_argument('uname')
        # pwd = self.get_body_argument('pwd')
        # favs = self.get_body_arguments('fav')
        pwd = self.get_argument('pwd')
        favs = self.get_arguments('fav')


        # 输出到页面显示
        self.write('%s,%s,%s' % (uname, pwd, favs))


#创建应用
app = tornado.web.Application([
    (r'/',IndexHandler),
    (r'/login/',LoginHandler),
])

#绑定地址和端口号
app.listen(8000)

#启动服务器不断监听端口是否有请求
tornado.ioloop.IOLoop.current().start()