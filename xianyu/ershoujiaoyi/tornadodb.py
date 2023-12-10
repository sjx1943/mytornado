import tornado.ioloop
import tornado.web
import tornado.escape

# 假设已经有了数据库连接和相关ORM模型

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id: return None
        return User.get(user_id)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("Hello, " + self.current_user.name)

class RegisterHandler(BaseHandler):
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        # 这里应该有更多的验证和加密步骤
        user = User.create(username=username, password=password)
        self.set_secure_cookie("user_id", str(user.id))
        self.redirect("/")

class ItemHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument("title")
        description = self.get_argument("description")
        price = self.get_argument("price")
        # 这里应该有更多的验证和存储步骤
        item = Item.create(owner=self.current_user, title=title, description=description, price=price)
        self.write({"id": item.id, "message": "Item created successfully."})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/register", RegisterHandler),
        (r"/item", ItemHandler),
    ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    login_url = "/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
