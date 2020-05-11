from hashlib import sha256
from sqlalchemy import Column, String
from models import BaseModel, db
from secret import salt


class User(BaseModel, db.Model):
    username = Column(String(50), nullable=False)
    password = Column(String(256), nullable=False)

    @staticmethod
    def salted_password(password: str) -> str:
        password = sha256(password.encode('ascii')).hexdigest()
        salted = password + salt
        hashed = sha256(salted.encode('ascii')).hexdigest()
        return hashed

    @staticmethod
    def username_check(username: str) -> tuple:
        user = User.one(username=username)
        if user is not None:
            result = '该用户名已存在'
            return False, result
        status = username.find(' ')
        if status != -1:
            result = '用户名不允许包含空格'
            return False, result
        length = len(username)
        if length < 2:
            result = '用户名长度必须大于2'
            return False, result
        return True, ''

    @classmethod
    def login(cls, form: dict):
        username: str = form['username']
        password: str = form['password']
        salted = cls.salted_password(password)
        user = User.one(username=username, password=salted)
        if user is not None:
            return user

    @classmethod
    def register(cls, form: dict):
        username: str = form['username']
        password: str = form['password']
        status, result = cls.username_check(username)
        if status:
            d = dict(
                username=username,
                password=cls.salted_password(password),
            )
            user = User.new(d)
            return user
