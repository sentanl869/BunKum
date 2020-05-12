from models import BaseModel, db
from models.user import User
from sqlalchemy import Column, Integer, Unicode, UnicodeText


class Blog(BaseModel, db.Model):
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)

    @classmethod
    def add(cls, form: dict, user):
        title = form['title']
        content = form['content']
        u = user
        form = dict(
            title=title,
            content=content,
            user_id=u.id
        )
        Blog.new(form)

    def author(self):
        u = User.one(id=self.user_id)
        return u.username
