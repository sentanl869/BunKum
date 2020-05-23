from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from models.user import User


main = Blueprint('user', __name__, url_prefix='/user')


@main.route('/login/view')
def login_view() -> bytes:
    return render_template('login.html')


@main.route('/login', methods=['POST'])
def login() -> bytes:
    form = request.form
    user, result = User.login(form)
    if user is None:
        return render_template('login.html', result=result)
    else:
        session['user_id'] = user.id
        res = session.pop('redirect')
        if res:
            return redirect(res)
        else:
            return redirect(url_for('blog.index'))


@main.route('/register/view')
def register_view() -> bytes:
    return render_template('register.html')


@main.route('/register', methods=['POST'])
def register() -> bytes:
    form = request.form
    user, result = User.register(form)
    if user is None:
        return render_template('register.html', result=result)
    else:
        session['user_id'] = user.id
        res = session.pop('redirect')
        if res:
            return redirect(res)
        else:
            return redirect(url_for('blog.index'))
