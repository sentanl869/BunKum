from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer
from time import time


db = SQLAlchemy()


class BaseModel:
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_time = Column(Integer, default=int(time()))
    updated_time = Column(Integer, default=int(time()))

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def new(cls, form: dict):
        m = cls()
        for name, value in form.items():
            setattr(m, name, value)
        m.save()
        return m

    @classmethod
    def update(cls, _id: int, **kwargs):
        m = cls.query.filter_by(id=_id).first()
        for name, value in kwargs.items():
            setattr(m, name, value)
        m.save()

    @classmethod
    def all(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).all()
        return ms

    @classmethod
    def one(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).first()
        return ms
