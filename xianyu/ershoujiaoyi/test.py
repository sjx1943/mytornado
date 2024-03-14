#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import time
from datetime import timedelta

from html.parser import HTMLParser
from urllib.parse import urljoin, urldefrag
import uuid,smtplib
from email.mime.text import MIMEText

import tornado
from tornado import gen, httpclient, queues
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, RedirectHandler
import re
import asyncio
import tornado
# from web import db
from tornado import template
import redis
import secrets

from email.mime.multipart import MIMEMultipart

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
    subject = "Reset Your Password"
    body = f"Please click on the following link to reset your password: {reset_link}"

    send_email(email, subject, body)


send_reset_email("sjx.1943@163.com", 20240314)

