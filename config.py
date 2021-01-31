import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ADMIN_ACCOUNT = os.environ.get('ADMIN_ACCOUNT')
    DEFAULT_AVATAR_FILE_NAME = os.environ.get('DEFAULT_AVATAR_FILE_NAME')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    BOOTSTRAP_CDN_FORCE_SSL = True

    POSTS_PER_PAGE = 6
    COMMENTS_PER_PAGE = 15
    ADMIN_PER_PAGE = 20

    AVATARS_RELATIVE_PATH = os.path.join(
        os.sep, 'static', 'avatars'
    )
    AVATARS_ABSOLUTE_PATH = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'static',
            'avatars'
        )
    )

    MAIL_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_SUBJECT_PREFIX = '[BunKum]'

    @classmethod
    def init_app(cls, app) -> None:
        from flask_bootstrap import (
            ConditionalCDN,
            WebCDN,
            JQUERY_VERSION,
            BOOTSTRAP_VERSION,
            HTML5SHIV_VERSION,
            RESPONDJS_VERSION,
        )
        from jinja2 import Markup

        static = app.extensions['bootstrap']['cdns']['static']
        local = app.extensions['bootstrap']['cdns']['local']

        def change_url(target_lib: str, target_version: str, fallback) -> None:
            content_text = 'dist'
            if target_lib == 'respond.js':
                content_text = 'dest'
            target_url = ConditionalCDN(
                'BOOTSTRAP_SERVE_LOCAL',
                fallback,
                WebCDN(
                    f'//cdn.jsdelivr.net/npm/{target_lib}@{target_version}/{content_text}/'
                )
            )
            app.extensions['bootstrap']['cdns'][target_lib] = target_url

        libs = {
            'jquery': {
                'version': JQUERY_VERSION,
                'fallback': local,
            },
            'bootstrap': {
                'version': BOOTSTRAP_VERSION,
                'fallback': local,
            },
            'html5shiv': {
                'version': HTML5SHIV_VERSION,
                'fallback': static,
            },
            'respond.js': {
                'version': RESPONDJS_VERSION,
                'fallback': static,
            },
        }

        for k, v in libs.items():
            change_url(k, v['version'], v['fallback'])

        class _pagedown(object):
            def include_pagedown(self):
                return Markup('''
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/pagedown@1.0.0/Markdown.Converter.js"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/pagedown@1.0.0/Markdown.Sanitizer.js"></script>
        ''')

            def html_head(self):
                return self.include_pagedown()

        app.extensions['pagedown'] = _pagedown()


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(
        os.environ.get('db_user'),
        os.environ.get('MYSQL_PASSWORD'),
        os.environ.get('db_host'),
        os.environ.get('db_name'),
    )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(Config):
    DATABASE_HOST = os.environ.get('db_host')
    if os.environ.get('DOCKER'):
        DATABASE_HOST = os.environ.get('DOCKER_DB_HOST')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(
        os.environ.get('db_user'),
        os.environ.get('MYSQL_PASSWORD'),
        DATABASE_HOST,
        os.environ.get('db_name'),
    )

    @classmethod
    def init_app(cls, app) -> None:
        Config.init_app(app)

        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class CeleryAppConfig:
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_SSL = True


class CeleryConfig:
    if os.environ.get('DOCKER'):
        broker_url = os.environ.get('DOCKER_CELERY_BROKER_URL')
        result_backend = os.environ.get('DOCKER_CELERY_RESULT_BACKEND')
    else:
        broker_url = os.environ.get('CELERY_DEFAULT_BROKER_URL')
        result_backend = os.environ.get('CELERY_DEFAULT_RESULT_BACKEND')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'celery': CeleryAppConfig,
    'default': DevelopmentConfig,
}
