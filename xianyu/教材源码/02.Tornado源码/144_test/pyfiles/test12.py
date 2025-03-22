#coding=utf-8
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
import os
from tornado.template import Template
class Person(object):
    def __init__(self,pname):
        self.pname = pname

def reverse(obj):
    if isinstance(obj,list):
        obj.reverse()
    return obj

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        l = ['a1','a2','a3']

        d = {'k1':'v1','k2':'v2','k3':'v3'}

        p = Person('xiaoming')

        s = '<h1>中国</h1>'
        s1 = '<script>location.href="https://www.baidu.com"</script>'

        self.render('temp1.html',uname='wangwu',l=l,d=d,p=p,rev=reverse,s=s,s1=s1)

app = Application([
    (r'/index',IndexHandler)
],template_path=os.path.join(os.getcwd(),'templates'))

if __name__ == '__main__':
    app.listen(8000)
    IOLoop.current().start()


