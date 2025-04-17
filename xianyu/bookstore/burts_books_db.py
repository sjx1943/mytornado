#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import tornado.locale
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from pymongo import MongoClient

define("port", default=8000, help="run on the given port", type=int)



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title = "Burt's Books | Home",
            header_text = "Welcome to Burt's Books!",
        )

class RecommendedHandler(tornado.web.RequestHandler):
    def get(self):
        coll = self.application.db.books

        books = coll.find()
        self.render(
            "recommended.html",
            page_title = "Burt's Books | Recommended Reading",
            header_text = "推荐读物",
            books = books,

        )

class BookModule(tornado.web.UIModule):
    def render(self, book):
        return self.render_string(
            "mymodule/book.html",
            book=book,
        )
    def css_files(self):
        return "/static/css/recommended.css"
    def javascript_files(self):
        return "/static/js/recommended.js"

class BookEditHandler(tornado.web.RequestHandler):
    def get(self, isbn=None):
        book = dict()
        if isbn:
            coll = self.application.db.books
            book = coll.find_one({"isbn": isbn})
        self.render("book_edit.html",
            page_title="Burt's Books",
            header_text="添加图书信息",
            book=book)

    def post(self, isbn=None):
        import time
        book_fields = ['isbn', 'title', 'subtitle', 'image', 'author',
            'date_released', 'description']
        coll = self.application.db.books
        book = dict()
        if isbn:
            book = coll.find_one({"isbn": isbn})
        for key in book_fields:
            book[key] = self.get_argument(key, None)

        if isbn:
            coll.replace_one({"isbn": isbn}, book)
        else:
            book['date_added'] = int(time.time())
            coll.insert_one(book)
        self.redirect("/recommended/")


settings = {
    'template_path': os.path.join(os.path.dirname(__file__), "mytemplate"),
    'static_path': os.path.join(os.path.dirname(__file__), "mystatics"),
    'ui_modules': {"Book": BookModule},
    'debug': True,
    'login_url': "/login",
    'cookie_secret': 'sjxxx',
    'xsrf_cookies': False
}


def make_app():
    conn = MongoClient("localhost", 27017)
    db = conn["bookstore"]

    handlers = [
        (r"/", MainHandler),
        (r"/recommended/", RecommendedHandler),
        (r"/edit/([0-9Xx\-]+)/?", BookEditHandler),
        (r"/add", BookEditHandler),
        (r"/mystatics/(.*)", tornado.web.StaticFileHandler,
         {"path": settings['static_path']})
    ]

    app = tornado.web.Application(handlers, **settings)
    app.db = db  # 将db实例附加到app上
    return app



if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    print("服务器已启动，监听端口:", options.port)
    tornado.ioloop.IOLoop.current().start()