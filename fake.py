import os
from time import time
from random import randint

from sqlalchemy.exc import IntegrityError
from faker import Factory

from models.helper import db
from models.user import User
from models.blog import Blog
from models.comment import Comment
from models.category import Category
from models.message import Message


def fake_users(count=100) -> None:
    start_time = time()
    fake = Factory.create('zh_CN')
    i = 0
    while i < count:
        user = User(
            email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    end_time = time()
    print(f'fake_users cost {(end_time - start_time)} seconds.')


def fake_categories(count=30) -> None:
    start_time = time()
    fake = Factory.create('zh_CN')
    i = 0
    while i < count:
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
    end_time = time()
    print(f'fake_categories cost {(end_time - start_time)} seconds.')


def fake_posts(count=100) -> None:
    start_time = time()
    fake = Factory.create('zh_CN')
    user = User.one(email=os.environ.get('ADMIN_ACCOUNT'))
    categories_count = Category.count()
    for _ in range(count):
        category = Category.offset(randint(0, categories_count - 1))
        post_dict = {
            'title': fake.sentence(),
            'content': fake.text() + fake.text() + fake.text(),
            'category': category
        }
        Blog.add(post_dict, user)
    end_time = time()
    print(f'fake_posts cost {(end_time - start_time)} seconds.')


def fake_comments(count=30) -> None:
    start_time = time()
    fake = Factory.create('zh_CN')
    user_count = User.count()
    blogs = Blog.all()
    for post in blogs:
        for _ in range(count):
            user = User.offset(randint(0, user_count - 1))
            form_dict = {
                'content': fake.text()
            }
            Comment.add(form_dict, user, post)
    end_time = time()
    print(f'fake_comments cost {(end_time - start_time)} seconds.')


def fake_messages(count=100) -> None:
    start_time = time()
    fake = Factory.create('zh_CN')
    user = User.one(email=os.environ.get('ADMIN_ACCOUNT'))
    user_count = User.count()
    for _ in range(count):
        author = User.offset(randint(0, user_count - 1))
        receiver = user
        form_dict = {
            'content': fake.text()
        }
        Message.add(form_dict, author, receiver)
    for _ in range(count):
        author = user
        receiver = User.offset(randint(0, user_count - 1))
        form_dict = {
            'content': fake.text()
        }
        Message.add(form_dict, author, receiver)
    end_time = time()
    print(f'fake_messages cost {(end_time - start_time)} seconds.')


def fake_all() -> None:
    start_time = time()
    fake_users()
    fake_categories()
    fake_posts()
    fake_comments()
    fake_messages()
    end_time = time()
    print(f'Total cost {(end_time - start_time)} seconds.')
