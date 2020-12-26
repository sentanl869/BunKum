from sqlalchemy import Column, Text, Integer, Boolean, ForeignKey

from models import BaseModel
from models.helper import db, safe_markdown


class Comment(BaseModel, db.Model):
    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    disabled = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    blog_id = Column(Integer, ForeignKey('blogs.id'))

    @classmethod
    def add(cls, form: dict, user, blog) -> None:
        content_html = safe_markdown(form['content'])
        cls.new(
            content=form['content'],
            content_html=content_html,
            blog=blog,
            author=user
        )
