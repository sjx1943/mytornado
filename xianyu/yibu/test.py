#!/usr/bin/env python
# -*- coding: utf-8 -*-

from robyn import Robyn

app = Robyn(__file__)

@app.get("/")
async def h(request):
    return "Hello, abc!"

app.start(port=8080)