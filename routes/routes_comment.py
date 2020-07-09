from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
)
from routes import (
    login_required,
    current_user,
    author_required,
)
from models.comment import Comment


main = Blueprint('comment', __name__, url_prefix='/comment')


@main.route('/add', methods=['POST'])
@login_required
def add():
    user = current_user()
    form = request.form
    Comment.add(form, user)
    return redirect(url_for('blog.detail', id=form['blog_id']))


@main.route('/delete', methods=['POST'])
@login_required
@author_required
def delete():
    blog_id = request.form['blog_id']
    comment_id = request.form['comment_id']
    Comment.delete(comment_id)
    return redirect(url_for('blog.detail', id=blog_id))
