from flask_bootstrap import Bootstrap
from flask_login import LoginManager, AnonymousUserMixin
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_pagedown import PageDown
from flask_wtf import CSRFProtect


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
