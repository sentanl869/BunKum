from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey

from models import BaseModel
from models.helper import db, safe_markdown


class Message(BaseModel, db.Model):
    __tablename__ = 'messages'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    author_delete = Column(Boolean, default=False)
    receiver_delete = Column(Boolean, default=False)
    notification = Column(Boolean, default=False)
    bolg_id = Column(Integer, ForeignKey('blogs.id'))
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
    def edit(cls, form: dict, message) -> None:
        if form.get('author_delete') and form.get('receiver_delete'):
            message.remove()
        else:
            content_html = safe_markdown(form['content'])
            cls.update(
                message,
                content=form['content'],
                content_html=content_html,
                author_delete=form['author_delete'],
                receiver_delete=form['receiver_delete']
            )

    def unilateral_delete(self, form: dict) -> None:
        if form.get('author_delete'):
            self.author_delete = True
        elif form.get('receiver_delete'):
            self.receiver_delete = True
        self.save()
        if self.author_delete and self.receiver_delete:
            self.remove()

    @classmethod
    def auto_notification(cls, content: str, author, receivers: list, blog) -> None:
        for receiver in receivers:
            content_html = safe_markdown(content)
            cls.new(
                notification=True,
                author_delete=True,
                content=content,
                content_html=content_html,
                author=author,
                receiver=receiver,
                blog=blog
            )

    @classmethod
    def unread_message_count(cls, *args, **kwargs) -> int:
        ms = cls.query.filter_by(**kwargs).filter(*args).count()
        return ms
