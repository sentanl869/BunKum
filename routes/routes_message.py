from flask import (
    Blueprint,
    request,
    current_app,
    render_template,
    flash,
    redirect,
    url_for,
    abort,
)
from flask_login import login_required, current_user

from routes import current_user_object
from models.forms import MessageForm
from models.user import User
from models.message import Message


main = Blueprint('message', __name__, url_prefix='/message')


@main.route('/inbox')
@login_required
def inbox_index() -> bytes:
    current_user.read()
    page = request.args.get('page', 1, type=int)
    pagination = current_user.messages_received_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Message.id.desc()
    )
    messages = pagination.items
    return render_template(
        'message_inbox.html',
        messages=messages,
        pagination=pagination,
        page=page,
        next=request.full_path
    )


@main.route('/outbox')
@login_required
def outbox_index() -> bytes:
    page = request.args.get('page', 1, type=int)
    pagination = current_user.messages_sent_page(
        page,
        current_app.config['ADMIN_PER_PAGE'],
        Message.id.desc()
    )
    messages = pagination.items
    return render_template(
        'message_outbox.html',
        messages=messages,
        pagination=pagination,
        page=page,
        next=request.full_path
    )


@main.route('/to/<username>', methods=['GET', 'POST'])
@login_required
def new(username: str) -> bytes:
    form = MessageForm()
    if form.validate_on_submit():
        author = current_user_object(current_user.id)
        receiver = User.one(username=username)
        form_dict = {
            'content': form.content.data
        }
        Message.add(form_dict, author, receiver)
        flash('您的消息发送成功！')
        return redirect(url_for('message.outbox_index'))
    return render_template('new_message.html', form=form)


@main.route('/delete', methods=['POST'])
@login_required
def delete() -> bytes:
    form = request.form
    message = Message.one(id=form['_id'])
    if message is None:
        abort(404)
    message.unilateral_delete(form)
    flash('消息删除成功！')
    target_url: str = form['next']
    if target_url is None or not target_url.startswith('/'):
        target_url = url_for('message.inbox_index')
    return redirect(target_url)
