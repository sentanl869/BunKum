from sqlalchemy import Column, Text, Integer, ForeignKey

from models import BaseModel
from models.helper import db, safe_markdown


class Message(BaseModel, db.Model):
    __tablename__ = 'messages'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))

    @classmethod
    def add(cls, form: dict, author, receiver) -> None:
        content_html = safe_markdown(form['content'])
        cls.new(
            content=form['content'],
            content_html=content_html,
            author=author,
            receiver=receiver
        )

    @classmethod
    def unread_message_count(cls, *args, **kwargs) -> int:
        ms = cls.query.filter_by(**kwargs).filter(*args).count()
        return ms
