from flask import Flask
from routes.routes_index import main as index_route


def register_routes(app):
    app.register_blueprint(index_route)


def configured_app():
    app = Flask(__name__)
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
