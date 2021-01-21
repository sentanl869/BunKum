from functools import wraps

from flask import abort
from flask_login import current_user

from models.role import Permission


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
