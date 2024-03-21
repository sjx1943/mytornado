from typing import Optional, Awaitable

import tornado


class MainHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("user")
        # 获取用户信息、推荐商品等...
    def prepare(self):
        if not self.current_user:
            self.redirect("/login")
            return
    def get(self):
        username = self.current_user
        # self.write("已经成功登陆"+username)
        self.render("main_page.html", username=username)