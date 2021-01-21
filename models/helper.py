from flask import (
    current_app,
    render_template,
    url_for,
)
from flask_login import current_user

from models.user import User
from models.message import Message
from tasks import async_send_email


def send_email(to: str, subject: str, template: str, **kwargs) -> None:
    form_dict = {
        'subject': current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
        'sender': current_app.config['MAIL_SENDER'],
        'recipients': [to],
        'body': render_template(template + '.txt', **kwargs),
        'html': render_template(template + '.html', **kwargs)
    }
    async_send_email.delay(form_dict)


def current_user_object(_id: int) -> User:
    return User.one(id=_id)


def content_at_processing(content: str, blog) -> str:
    parts = content.split()
    receivers = []
    for part in parts:
        if part.startswith('@'):
            username = part[1:]
            user = User.one(username=username)
            if user is not None and user not in receivers:
                receivers.append(user)
                content = content.replace(
                    part,
                    f"[@{username}]({url_for('user.profile', username=username)})",
                )
    if receivers:
        author = current_user_object(current_user.id)
        Message.auto_notification(content, author, receivers, blog)
    return content
