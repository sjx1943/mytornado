#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
from datetime import timedelta

from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag
import socket
import tornado
from tornado.queues import Queue, PriorityQueue
from tornado import gen, httpclient, queues
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, RedirectHandler
from tornado.locks import Event, Condition
import asyncio
import tornado
# from web import db
from tornado import template
t = template.Template("<html>{{ myvalue }}</html>")
print(t.generate(myvalue="XXSX"))

class MainHandler(RequestHandler):
    def get(self):
        items = ["Item 1", "Item 2", "Item 3"]
        self.render("mystatics.html", title="My titlesjx", items=items)

class StoryHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, story_id):
        self.write("this is story %s" % story_id)


class MyFormHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/myform" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')
    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))

class MMainHandler(tornado.web.RequestHandler):
    async def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        response = await http.fetch("http://google.com")
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
def make_app():
    return Application([
        url(r"/", MainHandler),
        # url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story"),
        url(r"/myform",MyFormHandler),
        url(r"/diaotou",RedirectHandler,dict(url="http://baidu.com")),
        url(r"/api",MMainHandler)
    ],template_path = 'mytemplate',)

# async def main():
#     app = make_app()
#     app.listen(8888)
#     shutdown_event = asyncio.Event()
#     await shutdown_event.wait()
#
# if __name__ == "__main__":
#     asyncio.run(main())


async def main():
    q = PriorityQueue()
    q.put((1, 'medium-priority item'))
    q.put((0, 'high-priority item'))
    q.put((-100, 'low-priority item'))

    print(await q.get())
    print(await q.get())
    print(await q.get())

asyncio.run(main())