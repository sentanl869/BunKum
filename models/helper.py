from flask import (
    current_app,
    render_template,
    url_for,
)
from flask_login import current_user
from markdown import Markdown
from bleach import linkify, clean

from models.user import User
from models.message import Message
from models.extensions import login_manager
from tasks import async_send_email


@login_manager.user_loader
def load_user(user_id) -> User:
    return User.one(id=int(user_id))


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


def get_size(file) -> int:
    position = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(position)
    return size


def markdown_covered(content: str) -> str:
    markdown = Markdown(
        extensions=['extra', 'fenced_code', 'tables', 'toc']
    )
    markdown_content = markdown.convert(content)
    return markdown_content


def safe_markdown(content: str) -> str:
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
        'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'kbd', 'table',
        'thead', 'tr', 'th', 'td', 'tbody', 'hr', 'img',
    ]
    allowed_attributes = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['alt'],
        'abbr': ['title'],
        'acronym': ['title'],
    }
    markdown_content = markdown_covered(content)
    safe_content = linkify(
        clean(
            markdown_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    )
    return safe_content
