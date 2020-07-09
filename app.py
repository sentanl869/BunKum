from flask import Flask
from datetime import timedelta
from secret import mysql_password, secret_key
from models import db
from routes.routes_blog import main as blog_route
from routes.routes_user import main as user_route
from routes.routes_comment import main as comment_route
import db_config


def register_routes(app):
    app.register_blueprint(blog_route)
    app.register_blueprint(user_route)
    app.register_blueprint(comment_route)


def configured_app():
    app = Flask(__name__)
    app.secret_key = secret_key
    uri = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(
        db_config.db_user,
        mysql_password,
        db_config.db_host,
        db_config.db_name,
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    db.init_app(app)
    register_routes(app)
    return app


if __name__ == '__main__':
    _app = configured_app()
    config = dict(
        debug=True,
        host='127.0.0.1',
        port=3000,
        threaded=True,
    )
    _app.run(**config)
