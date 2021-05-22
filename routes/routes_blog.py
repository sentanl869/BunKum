from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
from flask_login import current_user, login_required

from routes import admin_required
from models.blog import Blog
from models.comment import Comment
from models.category import Category
from models.forms import PostForm, CommentForm
from models.helper import current_user_object, content_at_processing


main = Blueprint('blog', __name__)


@main.route('/')
def index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Blog.page(
        page,
        current_app.config['POSTS_PER_PAGE'],
        Blog.id.desc()
    )
    posts = pagination.items
    categories = Category.order(Category.id)
    return render_template(
        'index.html',
        posts=posts,
        pagination=pagination,
        categories=categories
    )


@main.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new() -> bytes:
    form = PostForm()
    if form.validate_on_submit():
        user = current_user_object(current_user.id)
        category = Category.get(form.category.data)
        if form.new_category.data:
            category = Category.add(form.new_category.data)
        form_dict = {
            'title': form.title.data,
            'content': form.content.data,
            'category': category
        }
        Blog.add(form_dict, user)
        flash('新博客发布成功！')
        return redirect(url_for('blog.index'))
    return render_template('new_blog.html', form=form)


@main.route('/edit/<int:_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(_id: int) -> bytes:
    blog = Blog.one(id=_id)
    if blog is None:
        abort(404)
    form = PostForm()
    if form.validate_on_submit():
        category = Category.get(form.category.data)
        if form.new_category.data:
            category = Category.add(form.new_category.data)
        form_dict = {
            'title': form.title.data,
            'content': form.content.data,
            'category': category
        }
        Blog.edit(form_dict, blog)
        target_url: str = request.args.get('next')
        if target_url is None or not target_url.startswith('/'):
            target_url = url_for('blog.detail', _id=_id)
        flash('该篇博客更新完成。')
        return redirect(target_url)
    form.title.data = blog.title
    form.category.data = blog.category_id
    form.content.data = blog.content
    return render_template(
        'new_blog.html',
        form=form,
        next=request.full_path
    )


@main.route('/detail/<int:_id>', methods=['GET', 'POST'])
def detail(_id: int) -> bytes:
    blog = Blog.one(id=_id)
    form = CommentForm()
    if form.validate_on_submit():
        user = current_user_object(current_user.id)
        content = content_at_processing(form.content.data, blog)
        form_dict = {
            'content': content,
        }
        Comment.add(form_dict, user, blog)
        flash('您的评论发布成功！')
        return redirect(url_for('blog.detail', _id=_id))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = ((blog.comments.count() - 1) //
                current_app.config['COMMENTS_PER_PAGE'] + 1)
    pagination = blog.comments_page(
        page,
        current_app.config['COMMENTS_PER_PAGE'],
        Comment.created_time.asc()
    )
    comments = pagination.items
    categories = Category.order(Category.id)
    return render_template(
        'detail_blog.html',
        post=blog,
        form=form,
        comments=comments,
        categories=categories,
        pagination=pagination,
        page=page,
        next=request.full_path,
    )


@main.route('/delete', methods=['POST'])
@login_required
@admin_required
def delete() -> bytes:
    form = request.form
    blog = Blog.one(id=form['_id'])
    blog.delete_with_comments()
    flash('博客删除成功。')
    return redirect(url_for('blog.index'))


@main.route('/<name>')
def sort(name: str) -> bytes:
    category = Category.one(name=name)
    if category is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts_page(
        page,
        current_app.config['POSTS_PER_PAGE'],
        Blog.id.desc()
    )
    posts = pagination.items
    categories = Category.order(Category.id)
    return render_template(
        'index.html',
        name=name,
        endpoint='blog.sort',
        posts=posts,
        pagination=pagination,
        categories=categories
    )
