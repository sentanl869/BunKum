from flask import Blueprint, current_app, request, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries

from models.role import Permission


main = Blueprint('public', __name__)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                f'Slow query: {query.statement}\n'
                f'Parameters: {query.parameters}\n'
                f'Duration: {query.duration}s\n'
                f'Context: {query.context}\n'
            )
    return response


@main.before_app_request
def before_request() -> bytes:
    if current_user.is_authenticated:
        current_user.ping()
        if (not current_user.confirmed
                and request.endpoint
                and request.blueprint != 'user'
                and request.endpoint != 'static'):
            return redirect(url_for('user.unconfirmed'))


@main.app_context_processor
def inject_permission() -> dict:
    return {'Permission': Permission}
