from flask_bootstrap import Bootstrap
from flask_login import LoginManager, AnonymousUserMixin
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_wtf import CSRFProtect
from markdown import Markdown
from bleach import linkify, clean


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions) -> bool:
        return False

    def is_administrator(self) -> bool:
        return False


db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
pagedown = PageDown()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message = '请进行登录以继续访问该页面。'
login_manager.anonymous_user = AnonymousUser


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
