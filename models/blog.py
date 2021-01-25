from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models import BaseModel
from models.extensions import db
from models.helper import markdown_covered
from models.user import User


class Blog(BaseModel, db.Model):
    __tablename__ = 'blogs'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    title = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    comments = relationship('Comment', backref='blog', lazy='dynamic')
    notifications = relationship('Message', backref='blog', lazy='dynamic')

    @classmethod
    def add(cls, form: dict, user: User) -> None:
        content_html = markdown_covered(form['content'])
        cls.new(
            title=form['title'],
            category=form['category'],
            content=form['content'],
            content_html=content_html,
            author=user
        )

    @classmethod
    def edit(cls, form: dict, blog) -> None:
        content_html = markdown_covered(form['content'])
        cls.update(
            blog,
            title=form['title'],
            content=form['content'],
            content_html=content_html,
            category=form['category']
        )

    def delete_with_comments(self) -> None:
        comments = self.comments
        for comment in comments:
            comment.remove()
        self.remove()

    def comments_page(self, page: int, per_page: int, *args):
        ms = self.comments.order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms
