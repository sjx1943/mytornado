#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import tornado

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

async def main():
    app = make_app()
    app.listen(18888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
