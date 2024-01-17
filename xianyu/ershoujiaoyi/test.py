#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
from datetime import timedelta

from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag

import tornado
from tornado import gen, httpclient, queues
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, RedirectHandler
import re
import asyncio
import tornado
# from web import db
from tornado import template
import redis


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

def parse_time(time_str):
    # 正则表达式匹配小时、分钟和可选的AM/PM
    match = re.match(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str, re.I)
    if not match:
        raise ValueError("Invalid time format")

    # 从匹配的结果中提取小时、分钟和周期
    hours, minutes, period = match.groups()
    hours = int(hours)
    minutes = int(minutes) if minutes else 0
    period = period.lower() if period else None

    # 根据AM/PM调整小时数
    if period == 'am' and hours == 12:
        hours = 0
    elif period == 'pm' and hours != 12:
        hours += 12
    elif hours == 24:
        hours = 0

    # 返回总分钟数
    return hours * 60 + minutes

# 测试函数
print(parse_time("4pm"))       # 960
print(parse_time("7:38pm"))    # 1158
print(parse_time("23:42"))     # 1422
print(parse_time("3:16"))      # 196
print(parse_time("00:03"))    #2
