from os import getenv
from hashlib import sha256
from sqlalchemy import Column, String
from models import BaseModel, db


class User(BaseModel, db.Model):
    username = Column(String(50), nullable=False)
    password = Column(String(256), nullable=False)

    @staticmethod
    def salted_password(password: str) -> str:
        salt = getenv('salt')
        password = sha256(password.encode('ascii')).hexdigest()
        salted = password + salt
        hashed = sha256(salted.encode('ascii')).hexdigest()
        return hashed

    @staticmethod
    def register_check(username: str, password: str) -> tuple:
        user = User.one(username=username)
        if user is not None:
            error_code = '1'
            return False, error_code
        status = username.find(' ')
        if status != -1:
            error_code = '2'
            return False, error_code
        username_length = len(username)
        if username_length < 2:
            error_code = '3'
            return False, error_code
        password_length = len(password)
        if password_length < 2:
            error_code = '3'
            return False, error_code
        return True, ''

    @classmethod
    def login(cls, form: dict) -> tuple:
        username: str = form['username']
        password: str = form['password']
        salted = cls.salted_password(password)
        user = User.one(username=username, password=salted)
        if user is not None:
            return user, ''
        else:
            result = '用户名或密码错误'
            return None, result

    @classmethod
    def register(cls, form: dict) -> tuple:
        username: str = form['username']
        password: str = form['password']
        check_passed, error_code = cls.register_check(username=username, password=password)
        if check_passed:
            d = dict(
                username=username,
                password=cls.salted_password(password),
            )
            user = User.new(d)
            return user, ''
        else:
            error_message = {
                '1': '该用户名已存在',
                '2': '用户名不允许包含空格',
                '3': '用户名和密码长度必须大于2',
            }
            result = error_message.get(error_code, '未知错误')
            return None, result
