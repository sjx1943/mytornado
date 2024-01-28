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

        #你的 get 方法中，使用了 get_query_arguments('fav') 来获取 fav 参数的值，
        # 这意味着你应该在 URL 中使用 fav 作为参数名
        # 例如：http://localhost:8000/login/?uname=sjx&pwd=1234&fav=eat&fav=sleep

        #输出到页面显示
        #页面显示结果为  sjx, 1234, ['eat', 'sleep']
        self.write('%s,%s,%s'%(uname,pwd,favs))

    def post(self, *args, **kwargs):
        # 获取请求参数(POST请求方式)
        uname = self.get_body_argument('username')
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