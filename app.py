from flask import Flask
from secret import mysql_password, secret_key
from config import db_name
from models import db
from models.user import User
from models.blog import Blog
from routes.routes_index import main as index_route


def register_routes(app):
    app.register_blueprint(index_route)


def configured_app():
    app = Flask(__name__)
    app.secret_key = secret_key
    uri = 'mysql+pymysql://root:{}@localhost/{}?charset=utf8mb4'.format(
        mysql_password,
        db_name,
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
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
