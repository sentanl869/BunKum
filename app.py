from flask import Flask

from config import config
from models.extensions import (
    db, login_manager, bootstrap, moment, pagedown, csrf
)
from routes.routes_blog import main as blog_route
from routes.routes_user import main as user_route
from routes.routes_comment import main as comment_route
from routes.routes_admin import main as admin_route
from routes.routes_message import main as message_route


def register_routes(app: Flask) -> None:
    app.register_blueprint(blog_route)
    app.register_blueprint(user_route)
    app.register_blueprint(comment_route)
    app.register_blueprint(admin_route)
    app.register_blueprint(message_route)


def configured_app(config_name: str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    csrf.init_app(app)
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify()
        sslify.init_app(app)
    register_routes(app)
    config[config_name].init_app(app)
    return app
