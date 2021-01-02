from functools import wraps

from flask import abort, url_for
from flask_login import current_user

from models.user import User
from models.role import Permission
from models.message import Message


def permission_required(permission: int):
    def decorator(route_function):
        @wraps(route_function)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(404)
            return route_function(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(route_function):
    return permission_required(Permission.ADMIN)(route_function)


def current_user_object(_id: int) -> User:
    return User.one(id=_id)


def content_at_processing(content: str, blog) -> str:
    parts = content.split()
    receivers = []
    for part in parts:
        if part.startswith('@'):
            username = part[1:]
            user = User.one(username=username)
            if user is not None and user not in receivers:
                receivers.append(user)
                content = content.replace(
                    part,
                    f"[@{username}]({url_for('user.profile', username=username)})",
                )
    if receivers:
        author = current_user_object(current_user.id)
        Message.auto_notification(content, author, receivers, blog)
    return content
