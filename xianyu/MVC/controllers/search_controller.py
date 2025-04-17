#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
from models.product import Product
from tornado.escape import json_encode
from sqlalchemy import or_, func

class SearchHandler(RequestHandler):
    async def get(self):
        query = self.get_argument('q', '').strip()

        if not query:
            self.set_status(400)
            return self.write({'error': '搜索内容不能为空'})

        try:
            search_query = f"%{query}%"
            products = self.application.db.query(Product).filter(
                or_(
                    Product.name.ilike(search_query),
                    Product.description.ilike(search_query),
                    Product.tag.ilike(search_query)
                )
            ).all()

            self.write(json_encode([{
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'image': p.image,
                'tag': p.tag
            } for p in products]))

        except Exception as e:
            self.set_status(500)
            self.write({'error': str(e)})