# coding=utf-8
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask import jsonify
import time

db = SQLAlchemy(use_native_unicode="utf8")

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'router'

class User(UserMixin, db.Model):
    """用户"""
    __tablename__ = 'users'

    id = db.Column(db.String(20), doc='手机号码', primary_key=True)
    nickname = db.Column(db.String(20), doc='昵称', default='微聊用户', nullable=False)
    password_hash = db.Column(db.String(128), doc='密码散列值', nullable=False)
    sex = db.Column(db.String(5), doc='性别', default='未知', nullable=False)
    city = db.Column(db.String(10), doc='城市', default='未知城市', nullable=False)
    signature = db.Column(db.String(30), default='什么都没留下', doc='个性签名')
    avatar = db.Column(db.String(50), default='head.png', doc='用户头像', nullable=False)

    
    def __repr__(self):
        return '%s <%s>' % (self.nickname, self.id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'sex': self.sex,
            'city': self.city,
            'signature': self.signature,
            'avatar': '/static/image/' + self.avatar
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'code': 3, 'message': '需要先登录才能进行该操作'})

# 验证码
class verifyCode(object):
    def __init__(self, email, code):
        self.email = email
        self.time = time.time()
        self.code = code

    def verify(self, email, code):
        if code == self.code and email == self.email and not self.outOfDate():
            return True
        else:
            return False

    def outOfDate(self):
        return time.time() - self.time > 600