import tornado


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        username = self.get_current_user()
        if username is not None:
            self.render("main_page.html", username=username)
        else:
            self.redirect("/login")

    def get_current_user(self):
        return self.get_secure_cookie("user")
        # 获取用户信息、推荐商品等...