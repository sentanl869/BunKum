from flask import (
    Blueprint,
    request,
    current_app,
    render_template,
    abort,
    redirect,
    url_for,
)
from flask_login import login_required

from routes import permission_required
from models.role import Permission
from models.comment import Comment


main = Blueprint('comment', __name__, url_prefix='/comment')


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = Comment.page(
        page,
        current_app.config['COMMENTS_PER_PAGE'],
        Comment.id.desc()
    )
    comments = pagination.items
    return render_template(
        'moderate.html',
        comments=comments,
        pagination=pagination,
        page=page,
        next=request.full_path
    )


@main.route('/moderate/enable/<int:_id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(_id: int) -> bytes:
    page = request.args.get('page', 1, type=int)
    comment = Comment.one(id=_id)
    if comment is None:
        abort(404)
    comment.disabled = False
    comment.save()
    target_url: str = request.args.get('next')
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('comment.moderate', page=page)
    return redirect(target_url)


@main.route('/moderate/disable/<int:_id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(_id: int) -> bytes:
    page = request.args.get('page', 1, type=int)
    comment = Comment.one(id=_id)
    if comment is None:
        abort(404)
    comment.disabled = True
    comment.save()
    target_url: str = request.args.get('next')
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('comment.moderate', page=page)
    return redirect(target_url)
