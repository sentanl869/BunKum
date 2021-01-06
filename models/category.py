from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from models import BaseModel
from models.extensions import db


class Category(BaseModel, db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    posts = relationship('Blog', backref='category', lazy='dynamic')

    @staticmethod
    def insert_default_category() -> None:
        Category.new(
            name='未分类',
            default=True
        )

    @classmethod
    def add(cls, name: str):
        category = cls(name=name)
        category.save()
        return category

    def posts_page(self, page: int, per_page: int, *args):
        ms = self.posts.order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms

    def delete_with_posts(self) -> None:
        posts = self.posts
        if posts:
            for post in posts:
                post.category = Category.one(default=True)
                post.save()
        self.remove()
