import tornado


class ProductListHandler(tornado.web.RequestHandler):
    def get(self):
        pass

        # 获取商品列表...


class ProductDetailHandler(tornado.web.RequestHandler):
    def get(self, product_id):
        pass

        # 获取商品详情...
