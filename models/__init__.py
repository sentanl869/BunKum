from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
from time import time


db = SQLAlchemy()


class BaseModel:
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_time = Column(Integer, default=int(time()))
    updated_time = Column(Integer, default=int(time()))
