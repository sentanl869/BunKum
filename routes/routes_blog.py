from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)
from models.blog import Blog
from models.comment import Comment
from routes import (
    current_user,
    login_required,
)


main = Blueprint('blog', __name__)


@main.route('/')
def index() -> bytes:
    blogs = Blog.all()
    return render_template('index.html', blogs=blogs)


@main.route('/new')
@login_required
def new() -> bytes:
    return render_template('blog_new.html')


@main.route('/add', methods=['POST'])
@login_required
def add() -> bytes:
    user = current_user()
    form = request.form
    Blog.add(form, user)
    return redirect(url_for('blog.index'))


@main.route('/detail')
def detail() -> bytes:
    user = current_user()
    blog_id = request.args['id']
    blog = Blog.one(id=blog_id)
    comments = Comment.all(blog_id=blog_id)
    return render_template('blog_detail.html', blog=blog, comments=comments, user=user)
