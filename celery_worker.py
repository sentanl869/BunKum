from flask import Flask
from celery import Celery

from config import config
from models.extensions import mail


def configured_flask_app(config_name: str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    mail.init_app(app)
    return app


def configured_celery() -> Celery:
    flask_app = configured_flask_app('celery')
    celery_app = Celery('tasks')
    celery_app.conf.update(flask_app.config)
    task_base = celery_app.Task

    class ContextTask(task_base):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    setattr(celery_app, 'Task', ContextTask)
    return celery_app


celery = configured_celery()
