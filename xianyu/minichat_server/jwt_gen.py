import secrets
jwt_secret = secrets.token_urlsafe(32)  # 生成43个字符的安全随机字符串
print(jwt_secret)
