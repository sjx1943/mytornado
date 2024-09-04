import tornado.web
from sqlalchemy.orm import sessionmaker, scoped_session
from tornado.web import UIModule, StaticFileHandler
from models.user import User
from base.base import engine

import bcrypt
import uuid,smtplib,secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a session
Session = sessionmaker(bind=engine)
# session = Session()





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
        ms = self.get_argument('message',default=None)
        self.render("login.html", result=ms)

    async def post(self):
        # 在post方法中获取用户名和密码
        username = self.get_argument('username')
        password = self.get_argument('password')
        # 验证用户
        user = await self.validate_credentials(username,password)
        if user:
            # 如果验证成功，设置session并重定向到主页面
            self.set_secure_cookie("user", username)
            self.set_secure_cookie('user_id', str(user.id))
            self.redirect("/main")
        # if self.validate_credentials(username, password):
        #     # 如果验证成功，设置session并重定向到主页面
        #     self.set_secure_cookie("user", username)
        #     self.redirect("/main")
        else:
            # 如果验证失败，重新渲染登录页面并显示错误消息
            self.render("login.html", result="用户名或密码错误")
    async def validate_credentials(self, username, password):
        # 使用会话查询数据库并验证用户名和密码
        user = self.session.query(User).filter_by(username=username, password=password).first()
        return user


def generate_reset_token():
    """生成一个简单的重置令牌"""
    return secrets.token_urlsafe(16)

def send_email(to_email, subject, body):
    """发送电子邮件的简单实现"""
    msg = MIMEMultipart()
    msg['From'] = '363328084@qq.com'
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    server.login('363328084@qq.com', 'jluwcomlwzycbieb')
    text = msg.as_string()
    server.sendmail('363328084@qq.com', to_email, text)
    server.quit()


def send_reset_email(email, reset_token):
    """发送包含密码重置令牌的电子邮件"""
    reset_link = f"http://yourwebsite.com/reset_password?reset_token={reset_token}"
    subject = "密码重置"
    body = f"您的验证码为：\n\n {reset_token} \n\n请点击以下链接输入验证码和新密码进行密码重置： {reset_link}"

    send_email(email, subject, body)

class Forgotmodule(UIModule):
    def render(self, *args, **kwargs):
        ms = kwargs.get('result', '')
        return self.render_string('modules/forgot_module.html',ms="f module")

class ForgotPasswordHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()  # 创建新的会话

    def on_finish(self):
        self.session.close()  # 关闭会话

    def get(self):
        ms = self.get_argument('message',default=None)
        self.render("forgot_password.html",result=ms)
    def post(self):
        email = self.get_argument("email")
        user = self.session.query(User).filter_by(email=email).first()
        if user is not None:
            reset_token = generate_reset_token()
            user.reset_token = reset_token
            self.session.commit()
            send_reset_email(email, reset_token)
            self.render("token_input.html", result="请输入您的邮箱中的验证码和新密码")
        else:
            self.render("forgot_password.html", result="未查到关联邮箱，请核实后输入正确邮箱")

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

class ResetPasswordHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()  # 创建新的会话

    def on_finish(self):
        self.session.close()  # 关闭会话

    def post(self):
        reset_token = self.get_argument("reset_token")
        new_password = self.get_argument("new_password")
        user = self.session.query(User).filter_by(reset_token=reset_token).first()
        if user is not None:
            user.password = new_password  # 这是一个假设的函数，你需要实现它
            self.session.commit()
            self.render("password_reset_success.html")
        else:
            self.render("token_input.html", result="Invalid reset token，请核实后输入正确的邮箱验证码")

class Registmodule(UIModule):
    def render(self, *args, **kwargs):
        result = kwargs.get('result', '')
        return self.render_string('modules/register_module.html',result=result)

class RegisterHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = Session()  # 创建新的会话

    def on_finish(self):
        self.session.close()  # 关闭会话
    #
    def get(self):
        self.render("reg.html", result="")

    def post(self):
        # 处理登陆逻辑
        # 获取用户输入的用户名和密码
        username = self.get_argument("username")
        password = self.get_argument("password")
        email = self.get_argument("email")

        existing_user = self.session.query(User).filter_by(username=username).first()
        existing_email = self.session.query(User).filter_by(email=email).first()

        if existing_user is not None:
            self.render("reg.html", result="用户名已存在")
        elif existing_email is not None:
            self.render("reg.html", result="该邮箱已注册")
        else:
            # 创建新用户并添加到数据库
            new_user = User(username=username, password=password, email=email)
            self.session.add(new_user)
            try:
                self.session.commit()
                self.clear()
                self.redirect("/login?message=注册成功，请登录")
            except Exception as e:
                self.session.rollback()
                self.render("reg.html", result="Registration failed: " + str(e))



