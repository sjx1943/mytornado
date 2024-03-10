import tornado.web
from sqlalchemy.orm import sessionmaker, scoped_session
from tornado.web import UIModule, StaticFileHandler
from MVC.base.base import engine
from MVC.models.user import User

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


class Loginmodule(UIModule):
    def render(self, *args, **kwargs):
        result = kwargs.get('result', '')
        return self.render_string('modules/login_module.html', result=result)

class LoginHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()  # 创建新的会话

    def on_finish(self):
        self.session.close()  # 关闭会话

    def get(self):
        self.render("login.html", result="")

    def post(self):
        # 在post方法中获取用户名和密码
        username = self.get_argument('username')
        password = self.get_argument('password')
        # 验证用户
        if self.validate_credentials(username, password):
            # 如果验证成功，设置session并重定向到主页面
            self.set_secure_cookie("user", username)
            self.redirect("/main")
        else:
            # 如果验证失败，重新渲染登录页面并显示错误消息
            self.render("login.html", result="Invalid username or password")
    def validate_credentials(self, username, password):
        # 使用会话查询数据库并验证用户名和密码
        user = self.session.query(User).filter_by(username=username, password=password).first()
        return user is not None



class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        # 处理登陆逻辑
        # 获取用户输入的用户名和密码
        username = self.get_argument("username")
        password = self.get_argument("password")


