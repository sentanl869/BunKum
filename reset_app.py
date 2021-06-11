#!/usr/bin/env python3
import os
import shutil

from flask import current_app
from dotenv import load_dotenv
from sqlalchemy import create_engine

from service import app
from models.extensions import db


def recreate_database() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    db_name = os.environ.get('DB_NAME')
    db_host = os.environ.get('DB_HOST')
    if os.environ.get('DOCKER'):
        db_host = os.environ.get('DOCKER_DB_HOST')
    uri = 'mysql+pymysql://{}:{}@{}/?charset=utf8mb4'.format(
        os.environ.get('DB_USER'),
        os.environ.get('MYSQL_PASSWORD'),
        db_host,
    )
    engine = create_engine(uri, echo=True)
    with engine.connect() as c:
        c.execute(f'DROP DATABASE IF EXISTS {db_name};')
        c.execute(f'CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
        c.execute(f'USE {db_name};')
    db.metadata.create_all(bind=engine)


def reset_avatar() -> None:
    static_folder = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'static'
    )
    avatar_folder_path = current_app.config['AVATARS_ABSOLUTE_PATH']
    source_file_path = os.path.join(
        static_folder,
        current_app.config['DEFAULT_AVATAR_FILE_NAME']
    )
    if os.path.exists(avatar_folder_path):
        shutil.rmtree(avatar_folder_path)
    os.mkdir(avatar_folder_path)
    shutil.copy(source_file_path, avatar_folder_path)


if __name__ == '__main__':
    with app.app_context():
        recreate_database()
        reset_avatar()
