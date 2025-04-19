
# -*- coding: utf-8 -*-

import json
import time
import jwt
import requests
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.escape import json_encode, json_decode

# 微信小程序AppID和AppSecret
APPID = 'wxff27c7465f5e99bd'
APPSECRET = '8d5f677433c60a1f1543b219d2c560da'
JWT_SECRET = 'c21sgmT8K0lmuN8h9FvF7OuHCPmltH8UkhjmeCNEVpw'  # 自定义JWT签名密钥

# 保存所有连接的WebSocket客户端
clients = set()

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
        'exp': int(time.time()) + 3600 * 2  # 2小时有效期
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    # PyJWT 2.x 返回str，1.x返回bytes，兼容处理
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
            openid, session_key = get_openid_session(code)
            token = create_jwt(openid)
            self.finish({'token': token})
        except Exception as e:
            self.set_status(400)
            self.finish({'error': str(e)})

class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        # 允许跨域访问，生产环境请根据需求限制
        return True

    def open(self):
        # 从URL参数获取token
        token = self.get_argument('token', None)
        openid = verify_jwt(token)
        if not openid:
            self.close(code=4001, reason='认证失败')
            return
        self.openid = openid
        clients.add(self)
        print(f"用户 {openid} 已连接，当前连接数: {len(clients)}")

    def on_message(self, message):
        try:
            data = json.loads(message)
            # 附加发送者openid
            data['from'] = self.openid
            broadcast_msg = json.dumps(data)
            # 广播给所有连接客户端
            for client in clients:
                if client.ws_connection and client.ws_connection.is_active():
                    client.write_message(broadcast_msg)
        except Exception as e:
            print(f"消息处理异常: {e}")

    def on_close(self):
        clients.discard(self)
        print(f"用户 {getattr(self, 'openid', '未知')} 断开连接，当前连接数: {len(clients)}")

def make_app():
    return tornado.web.Application([
        (r"/api/login", LoginHandler),
        (r"/ws", ChatWebSocket),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5001)  # 监听5001端口，HTTP和WebSocket共用
    print("Tornado服务器启动，监听端口5001")
    tornado.ioloop.IOLoop.current().start()
