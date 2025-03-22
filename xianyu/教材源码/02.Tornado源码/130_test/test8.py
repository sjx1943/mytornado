#coding=utf-8


class BaseHandler(object):
    def initilize(self):
        print ('初始化方法')

    def get(self,*args,**kwargs):
        raise Exception(405)

    def post(self,*args,**kwargs):
        print('基类get方法')
        raise Exception(405)

    def on_finish(self):
        print ('请求处理结束')


class IndexHandler(BaseHandler):
    def initilize(self,conn):
        self.conn = conn
        print (conn)

    def get(self):
        print ('GET方式请求')


if __name__ == '__main__':
    urlpatterns=[
        (r'/index',IndexHandler,{'conn':'connection'})
    ]

    method = 'post'

    url = '/index'

    for r,v,d in urlpatterns:
        if url == r:
           vs = v()
           vs.initilize(d)
           if hasattr(vs,method):
               getattr(vs,method)()
           getattr(vs,'on_finish')()

