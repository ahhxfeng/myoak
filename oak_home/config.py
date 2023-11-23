#coding=utf-8

# DB_URI = "mysql+pymysql://think:123456@192.168.31.60/oak"
DB_URI = "mysql+pymysql://think:123456@localhost/oak?charset=utf8"

REDIS_HOST = "localhost"
REDIS_PORT = 6379
APP_FLASK_KEY = "OZyUa72B824FzrIG"

# 用户登录多久超时
JWT_EXPIRE = 60 * 60 * 2

# 跨域 : 只在调试阶段 使用
IS_ALLOW_ORIGIN = False