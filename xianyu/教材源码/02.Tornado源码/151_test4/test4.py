#coding=utf-8

from tornado.httpclient import AsyncHTTPClient
import os
from tornado.ioloop import IOLoop


def parse(con):
    import bs4
    bs = bs4.BeautifulSoup(con,'html.parser')
    h4List = [h4.text for h4 in bs.select('ul.foot_nav.main h4')]
    for h in h4List:
        print h



def handle_response(response):
    #获取页面内容
    content = response.body

    #写入到index.html页面中
    with open(os.path.join(os.getcwd(),'templates','index.html'),'wb') as fw:
        fw.write(content)

    #解析文档信息打印相关内容到控制台
    parse(content)



def loadPage(url,callback):
    #创建异步客户端
    asyncClient = AsyncHTTPClient()
    #获取页面内容
    asyncClient.fetch(url,callback=callback)

    print 'hello'

loadPage('http://www.bjsxt.com',handle_response)




IOLoop.instance().start()