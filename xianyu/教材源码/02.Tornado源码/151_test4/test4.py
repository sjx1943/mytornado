#coding=utf-8

# from tornado.httpclient import AsyncHTTPClient
# import os
# from tornado.ioloop import IOLoop
#
#
# def parse(con):
#     import bs4
#     bs = bs4.BeautifulSoup(con,'html.parser')
#     h4List = [h4.text for h4 in bs.select('ul.foot_nav.main h4')]
#     for h in h4List:
#         print (h)
#
#
#
# def handle_response(response):
#     #获取页面内容
#     content = response.body
#
#     #写入到index.html页面中
#     with open(os.path.join(os.getcwd(),'templates','index.html'),'wb') as fw:
#         fw.write(content)
#
#     #解析文档信息打印相关内容到控制台
#     parse(content)
#
#
#
# def loadPage(url,callback):
#     #创建异步客户端
#     asyncClient = AsyncHTTPClient()
#     #获取页面内容
#     asyncClient.fetch(url,callback=callback)
#
#     print('hello')
#
# loadPage('http://www.bjsxt.com',handle_response)
#
#
#
# IOLoop.instance().start()

from tornado.httpclient import AsyncHTTPClient, HTTPClientError
import os
from tornado.ioloop import IOLoop
import bs4

async def parse(con):
    bs = bs4.BeautifulSoup(con, 'html.parser')
    h4List = [h4.text for h4 in bs.select('ul.foot_nav.main h4')]
    for h in h4List:
        print(h)

async def handle_response(response):
    # 获取页面内容
    content = response.body if response.body else b''

    # 写入到index.html页面中
    with open(os.path.join(os.getcwd(), 'templates', 'index.html'), 'wb') as fw:
        fw.write(content)

    # 解析文档信息打印相关内容到控制台
    await parse(content)

async def loadPage(url):
    # 创建异步客户端
    asyncClient = AsyncHTTPClient()
    try:
        # 获取页面内容
        response = await asyncClient.fetch(url)
        await handle_response(response)
    except HTTPClientError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print('hello')

async def main():
    await loadPage('http://www.bjsxt.com')

if __name__ == "__main__":
    IOLoop.current().run_sync(main)
