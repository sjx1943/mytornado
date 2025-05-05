
# -*- coding: utf-8 -*-
import ssl
import json
import time
import jwt
import requests
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.escape import json_decode

APPID = 'wx4be72cc6e4cc1e59'
APPSECRET = '28d71914d9525c2403807a870e13b2f2'
JWT_SECRET = 'z8zZc9dmJ-NxncYMh7NIenqFUTjwVar1GUIxtHnHS2M'


clients = dict()  # {websocket: openid}

def get_openid_session(code):
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={APPSECRET}&js_code={code}&grant_type=authorization_code'
    resp = requests.get(url)
    data = resp.json()
    if 'openid' in data:
        return data['openid'], data.get('session_key')
    else:
        raise Exception('微信登录失败: ' + data.get('errmsg', '未知错误'))

def create_jwt(openid):
    payload = {
        'openid': openid,
        'exp': int(time.time()) + 3600 * 2
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['openid']
    except Exception:
        return None

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json_decode(self.request.body)
            code = data.get('code')
            if not code:
                self.set_status(400)
                self.finish({'error': '缺少code'})
                return
            openid, _ = get_openid_session(code)
            token = create_jwt(openid)
            self.finish({'token': token})
        except Exception as e:
            self.set_status(400)
            self.finish({'error': str(e)})

class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True  # 允许跨域

    def open(self):
        token = self.get_argument('token', None)
        openid = verify_jwt(token)
        if not openid:
            self.close(code=4001, reason='认证失败')
            return
        self.openid = openid
        clients[self] = openid
        print(f"用户 {openid} 已连接，当前连接数: {len(clients)}")
        # 广播用户加入消息
        self.broadcast_system_message(f"用户 {openid} 加入了聊天室le")

    def on_message(self, message):
        try:
            data = json.loads(message)
            data['from'] = self.openid
            data['timestamp'] = int(time.time())
            broadcast_msg = json.dumps({'type': 'chat', 'data': data})
            self.broadcast_message(broadcast_msg)
        except Exception as e:
            print(f"消息处理异常: {e}")

    def on_close(self):
        openid = clients.get(self, '未知')
        if self in clients:
            del clients[self]
        print(f"用户 {openid} 断开连接，当前连接数: {len(clients)}")
        self.broadcast_system_message(f"用户 {openid} 离开了聊天室")

    def broadcast_message(self, message):
        for client in clients:
            if client.ws_connection and client.ws_connection.stream and not client.ws_connection.stream.closed():
                client.write_message(message)

    def broadcast_system_message(self, content):
        msg = json.dumps({'type': 'system', 'data': {'content': content, 'timestamp': int(time.time())}})
        self.broadcast_message(msg)

def make_app():
    return tornado.web.Application([
        (r"/api/login", LoginHandler),
        (r"/ws", ChatWebSocket),
    ])



if __name__ == "__main__":
    app = make_app()
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(
        "/etc/letsencrypt/live/ser74785.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/ser74785.ddns.net/privkey.pem"
    )
    app.listen(5001, ssl_options=ssl_ctx)
    print("Tornado服务器启动，监听端口5001（HTTPS/WSS）")
    tornado.ioloop.IOLoop.current().start()


