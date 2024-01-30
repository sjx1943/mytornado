import tornado.web

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
