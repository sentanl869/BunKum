from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    url_for,
    redirect,
    abort,
)
from flask_login import login_required

from models.user import User
from models.blog import Blog
from models.role import Role
from models.category import Category
from models.comment import Comment
from models.message import Message
from models.forms import EditCategoryForm, EditCommentForm
from routes import admin_required


main = Blueprint('admin', __name__, url_prefix='/admin')


@main.route('/blog')
@login_required
@admin_required
def blog_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Blog.page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Blog.id.desc()
    )
    posts = pagination.items
    return render_template(
        'admin_index.html',
        posts=posts,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/blog/delete', methods=['POST'])
@login_required
@admin_required
def blog_delete() -> bytes:
    page = request.args.get('page', 1, type=int)
    form = request.form
    blog = Blog.one(id=form['_id'])
    if blog is None:
        abort(404)
    comments = blog.comments
    for comment in comments:
        comment.remove()
    blog.remove()
    target_url: str = form['next']
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('admin.index', page=page)
    flash('博客及其评论删除成功。')
    return redirect(target_url)


@main.route('/category')
@login_required
@admin_required
def category_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Category.page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Category.id.asc()
    )
    categories = pagination.items
    return render_template(
        'admin_category.html',
        categories=categories,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/edit/category/<int:_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def category_edit(_id: int) -> bytes:
    category = Category.one(id=_id)
    if category is None:
        abort(404)
    form = EditCategoryForm(category=category)
    if form.validate_on_submit():
        Category.update(
            category,
            name=form.name.data,
        )
        target_url: str = request.args.get('next')
        if target_url is None or not target_url.startswith('/'):
            target_url = url_for('admin.category_index')
        flash('博客分类条目已经更新。')
        return redirect(target_url)
    form.name.data = category.name
    return render_template(
        'edit_category.html',
        form=form,
        next=request.full_path
    )


@main.route('/category/delete', methods=['POST'])
@login_required
@admin_required
def category_delete() -> bytes:
    form = request.form
    category = Category.one(id=form['_id'])
    if category is None:
        abort(404)
    if category.default:
        abort(405)
    posts = category.posts
    if posts:
        for post in posts:
            post.category = Category.one(default=True)
            post.save()
    category.remove()
    target_url: str = form['next']
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('admin.category_index')
    flash('博客分类条目删除成功。')
    return redirect(target_url)


@main.route('/user')
@login_required
@admin_required
def user_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = User.page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        User.id.asc()
    )
    users = pagination.items
    return render_template(
        'admin_user.html',
        users=users,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/user/delete', methods=['POST'])
@login_required
@admin_required
def user_delete() -> bytes:
    form = request.form
    user = User.one(id=form['_id'])
    if user is None:
        abort(404)
    if user.is_administrator():
        abort(405)
    comments = user.comments
    if comments:
        for comment in comments:
            comment.remove()
    user.remove()
    target_url: str = form['next']
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('admin.user_index')
    flash('用户及其评论删除成功。')
    return redirect(target_url)


@main.route('/comment')
@login_required
@admin_required
def comment_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Comment.page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Comment.id.desc()
    )
    comments = pagination.items
    return render_template(
        'admin_comment.html',
        comments=comments,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/comment/edit/<int:_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def comment_edit(_id: int) -> bytes:
    comment = Comment.one(id=_id)
    if comment is None:
        abort(404)
    form = EditCommentForm()
    if form.validate_on_submit():
        form_dict = {
            'content': form.content.data,
            'disabled': form.disabled.data
        }
        Comment.edit(form_dict, comment)
        target_url: str = request.args.get('next')
        if target_url is None or not target_url.startswith('/'):
            target_url = url_for('admin.comment_index')
        flash('评论已经更新。')
        return redirect(target_url)
    form.content.data = comment.content
    form.disabled.data = comment.disabled
    return render_template(
        'edit_comment.html',
        form=form,
        next=request.full_path
    )


@main.route('/comment/delete', methods=['POST'])
@login_required
@admin_required
def comment_delete() -> bytes:
    form = request.form
    comment = Comment.one(id=form['_id'])
    if comment is None:
        abort(404)
    comment.remove()
    target_url: str = form['next']
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('admin.user_index')
    flash('评论删除成功。')
    return redirect(target_url)


@main.route('/comment/blog/<int:_id>')
@login_required
@admin_required
def comment_by_blog_index(_id: int) -> bytes:
    blog = Blog.one(id=_id)
    if blog is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = blog.comments_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Comment.id.desc()
    )
    comments = pagination.items
    return render_template(
        'admin_comment.html',
        _id=_id,
        endpoint='admin.comment_by_blog_index',
        comments=comments,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/comment/user/<username>')
@login_required
@admin_required
def comment_by_user_index(username: str) -> bytes:
    user = User.one(username=username)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.comments_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Comment.id.desc()
    )
    comments = pagination.items
    return render_template(
        'admin_comment.html',
        username=username,
        endpoint_by_user='admin.comment_by_user_index',
        comments=comments,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/blog/category/<name>')
@login_required
@admin_required
def blog_by_category_index(name: str) -> bytes:
    category = Category.one(name=name)
    if category is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Blog.id.desc()
    )
    posts = pagination.items
    return render_template(
        'admin_index.html',
        name=name,
        endpoint='admin.blog_by_category_index',
        posts=posts,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/user/role/<name>')
@login_required
@admin_required
def user_by_role_index(name: str) -> bytes:
    role = Role.one(name=name)
    if role is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = role.users_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        User.id.asc()
    )
    users = pagination.items
    return render_template(
        'admin_user.html',
        name=name,
        endpoint='admin.user_by_role_index',
        users=users,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/user/unconfirmed')
@login_required
@admin_required
def user_by_unconfirmed_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = User.filter_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        User.id.asc(),
        confirmed=False
    )
    users = pagination.items
    return render_template(
        'admin_user.html',
        users=users,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/comment/disabled')
@login_required
@admin_required
def comment_by_disabled_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Comment.filter_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Comment.id.desc(),
        disabled=True
    )
    comments = pagination.items
    return render_template(
        'admin_comment.html',
        comments=comments,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/message')
@login_required
@admin_required
def message_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Message.page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Message.id.desc()
    )
    messages = pagination.items
    return render_template(
        'admin_message.html',
        messages=messages,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/message/send/by/<username>')
@login_required
@admin_required
def message_send_by(username: str) -> bytes:
    user = User.one(username=username)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.messages_sent_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Message.id.desc()
    )
    messages = pagination.items
    return render_template(
        'admin_message.html',
        username=username,
        endpoint='admin.message_send_by',
        messages=messages,
        pagination=pagination,
        next=request.full_path
    )


@main.route('/message/send/for/<username>')
@login_required
@admin_required
def message_send_for(username: str) -> bytes:
    user = User.one(username=username)
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.messages_received_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Message.id.desc()
    )
    messages = pagination.items
    return render_template(
        'admin_message.html',
        username=username,
        endpoint='admin.message_send_for',
        messages=messages,
        pagination=pagination,
        next=request.full_path
    )
