from models import BaseModel, db
from sqlalchemy import Column, UnicodeText, Integer


class Comment(BaseModel, db.Model):
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    blog_id = Column(Integer, nullable=False)

    @classmethod
    def add(cls, form: dict, user):
        content: str = form['content']
        content = '\r\n' + content
        blog_id = form['blog_id']
        user_id = user.id
        form = dict(
            content=content,
            user_id=user_id,
            blog_id=blog_id,
        )
        cls.new(form)
