import os
from uuid import uuid4
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
    TimedJSONWebSignatureSerializer as Serializer,
)
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask import current_app
from flask_login import UserMixin

from models import BaseModel
from models.message import Message
from models.role import Role, Permission
from models.extensions import db, login_manager


class User(BaseModel, db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    email = Column(String(64), unique=True, index=True, nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    confirmed = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    avatar_url = Column(String(64), default=None)
    posts = relationship('Blog', backref='author', lazy='dynamic')
    comments = relationship('Comment', backref='author', lazy='dynamic')
    last_message_read_time = Column(DateTime, default=datetime.utcnow)
    messages_sent = relationship(
        'Message',
        foreign_keys=[Message.sender_id],
        backref='author',
        lazy='dynamic'
    )
    messages_received = relationship(
        'Message',
        foreign_keys=[Message.receiver_id],
        backref='receiver',
        lazy='dynamic'
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_ACCOUNT']:
                self.role = Role.one(name='Administrator')
            if self.role is None:
                self.role = Role.one(default=True)
        if self.avatar_url is None:
            self.avatar_url = os.path.join(
                current_app.config['AVATARS_RELATIVE_PATH'],
                current_app.config['DEFAULT_AVATAR_FILE_NAME']
            )

    @classmethod
    def register(cls, **kwargs):
        user = cls(**kwargs)
        user.save()
        return user

    @property
    def password(self) -> Exception:
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def can(self, perm: int) -> bool:
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self) -> bool:
        return self.can(Permission.ADMIN)

    def ping(self) -> None:
        self.last_seen = datetime.utcnow()
        self.save()

    def read(self) -> None:
        self.last_message_read_time = datetime.utcnow()
        self.save()

    def avatar_delete(self) -> None:
        filename = self.avatar_url.split(os.sep)[-1]
        avatar_path = os.path.join(
            current_app.config['AVATARS_ABSOLUTE_PATH'],
            filename
        )
        if os.path.exists(avatar_path) \
                and filename != \
                current_app.config['DEFAULT_AVATAR_FILE_NAME']:
            os.remove(avatar_path)

    def avatar_save(self, avatar_file) -> str:
        self.avatar_delete()
        suffix = avatar_file.filename.split('.')[-1]
        filename = f'{str(uuid4())}.{suffix}'
        avatar_path = os.path.join(
            current_app.config['AVATARS_ABSOLUTE_PATH'],
            filename
        )
        avatar_file.save(avatar_path)
        avatar_url = os.path.join(
            current_app.config['AVATARS_RELATIVE_PATH'],
            filename
        )
        return avatar_url

    def generate_confirmation_token(self, expiration=172800) -> str:
        token = Serializer(current_app.config['SECRET_KEY'], expiration)
        return token.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token: str) -> bool:
        identify_token = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = identify_token.loads(token.encode('utf-8'))
        except (BadSignature, BadTimeSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        self.save()
        return True

    def generate_email_change_token(self, new_email: str, expiration=86400) -> str:
        token = Serializer(current_app.config['SECRET_KEY'], expiration)
        return token.dumps(
            {
                'change_email': self.id,
                'new_email': new_email
            }
        ).decode('utf-8')

    def change_email(self, token: str) -> bool:
        identify_token = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = identify_token.loads(token.encode('utf-8'))
        except (BadSignature, BadTimeSignature, SignatureExpired):
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.one(email=new_email) is not None:
            return False
        self.email = new_email
        self.save()
        return True

    def generate_reset_token(self, expiration=900) -> str:
        token = Serializer(current_app.config['SECRET_KEY'], expiration)
        return token.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        identify_token = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = identify_token.loads(token.encode('utf-8'))
        except (BadSignature, BadTimeSignature, SignatureExpired):
            return False
        user = User.one(id=int(data.get('reset')))
        if user is None:
            return False
        user.password = new_password
        user.save()
        return True

    def delete_with_all(self) -> None:
        comments = self.comments
        if comments:
            for comment in comments:
                comment.remove()
        self.avatar_delete()
        self.remove()

    def comments_page(self, page: int, per_page: int, *args):
        ms = self.comments.order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms

    def messages_received_page(self, page: int, per_page: int, *args):
        ms = self.messages_received.filter_by(receiver_delete=False).order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms

    def messages_sent_page(self, page: int, per_page: int, *args):
        ms = self.messages_sent.filter_by(author_delete=False).order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms

    def unread_message_count(self) -> int:
        ms = Message.unread_message_count(
            Message.created_time > self.last_message_read_time,
            receiver=self
        )
        return ms


@login_manager.user_loader
def load_user(user_id) -> User:
    return User.one(id=int(user_id))
