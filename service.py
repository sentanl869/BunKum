#!/usr/bin/env python3
import os

from app import configured_app
from models.extensions import db
from models.user import User
from models.blog import Blog
from models.comment import Comment
from models.message import Message
from models.category import Category
from models.role import Role, Permission


app = configured_app('production')


@app.shell_context_processor
def make_shell_context() -> dict:
    return {
        'db': db,
        'User': User,
        'Blog': Blog,
        'Role': Role,
        'Comment': Comment,
        'Message': Message,
        'Category': Category,
        'Permission': Permission,
    }


@app.cli.command()
def deploy() -> None:
    Role.insert_roles()
    Category.insert_default_category()
    user = User(
        email=os.environ.get('ADMIN_ACCOUNT'),
        username=os.environ.get('ADMIN_USERNAME'),
        password=os.environ.get('ADMIN_PASSWORD'),
        confirmed=True
    )
    user.save()


if __name__ == '__main__':
    dev_app = configured_app('development')
    config = {
        'host': '127.0.0.1',
        'port': 3000
    }
    dev_app.run(**config)
