from flask import (
    session,
    redirect,
    url_for,
    request,
)
from functools import wraps
from models.user import User


def current_user():
    user_id = session.get('user_id', -1)
    u = User.one(id=user_id)
    return u


def login_required(route_function):
    @wraps(route_function)
    def r():
        u = current_user()
        if u is None:
            session['redirect'] = request.path
            return redirect(url_for('user.login_view'))
        else:
            return route_function()

    return r


def author_required(route_function):
    @wraps(route_function)
    def r():
        u = current_user()
        author_id = int(request.form['author_id'])
        if u is not None and u.id == author_id:
            return route_function()
        else:
            return redirect(url_for('user.login_view'))

    return r
