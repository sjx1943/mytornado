# chat_controller.py
import tornado.web
import tornado.websocket
import json
from models.product import Product
from sqlalchemy.orm import scoped_session, Session

user_sessions = {}


class ChatHandler(tornado.web.RequestHandler):
    def get(self):
        user_id = self.get_secure_cookie("user_id")
        self.render('chat_room.html', user_id=user_id)


class ChatWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.user_id = self.get_argument("user_id")
        self.product_id = self.get_argument("product_id", None)

        if self.product_id:
            session = scoped_session(Session)
            product = session.query(Product).filter(Product.id == self.product_id).first()
            if product is None:
                raise ValueError(f"No product found with id {self.product_id}")
            self.partner_id = product.user_id
            session.close()
            self.channel_id = f"{self.user_id}_{self.partner_id}" if int(
                self.user_id) < self.partner_id else f"{self.partner_id}_{self.user_id}"
        else:
            self.channel_id = 'public'

        if self.channel_id not in user_sessions:
            user_sessions[self.channel_id] = set()
        user_sessions[self.channel_id].add(self)

        self.write_message(f"Welcome to the chat room: {self.channel_id}")

    def on_message(self, message):
        try:
            message_data = json.loads(message)
            for user in user_sessions[self.channel_id]:
                user.write_message(f"{self.user_id} says: {message_data['content']}")
        except json.JSONDecodeError:
            self.write_message("Error: Invalid JSON format")

    def on_close(self):
        user_sessions[self.channel_id].remove(self)
        if not user_sessions[self.channel_id]:
            del user_sessions[self.channel_id]

    def check_origin(self, origin: str) -> bool:
        return True