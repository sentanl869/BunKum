from sqlalchemy import create_engine
from app import configured_app
from models import db
from secret import mysql_password
from config import db_name


def recreate_database():
    uri = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(
        mysql_password
    )
    engine = create_engine(uri, echo=True)
    with engine.connect() as c:
        c.execute('DROP DATABASE IF EXISTS {}'.format(db_name))
        c.execute('CREATE DATABASE {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'.format(db_name))
        c.execute('USE {}'.format(db_name))
    db.metadata.create_all(bind=engine)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        recreate_database()
