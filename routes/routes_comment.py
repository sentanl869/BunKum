from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
)
from routes import (
    login_required,
    current_user,
)
from models.comment import Comment


main = Blueprint('comment', __name__)


@main.route('/comment/add', methods=['POST'])
@login_required
def add():
    user = current_user()
    form = request.form
    Comment.add(form, user)
    return redirect(url_for('blog.detail', id=form['blog_id']))
