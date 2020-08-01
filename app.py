from flask import Flask
from dotenv import load_dotenv
from os import getenv
from datetime import timedelta
from models import db
from routes.routes_blog import main as blog_route
from routes.routes_user import main as user_route
from routes.routes_comment import main as comment_route


def register_routes(app):
    app.register_blueprint(blog_route)
    app.register_blueprint(user_route)
    app.register_blueprint(comment_route)


def configured_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = getenv('secret_key')
    uri = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(
        getenv('db_user'),
        getenv('mysql_password'),
        getenv('db_host'),
        getenv('db_name'),
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
