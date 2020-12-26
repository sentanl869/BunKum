from datetime import datetime

from sqlalchemy import Column, Integer, DateTime

from models.helper import db


class BaseModel:
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_time = Column(DateTime, default=datetime.utcnow)
    updated_time = Column(DateTime, default=datetime.utcnow)

    def save(self) -> None:
        self.updated_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def remove(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def new(cls, **kwargs) -> None:
        m = cls()
        for name, value in kwargs.items():
            setattr(m, name, value)
        m.save()

    @classmethod
    def update(cls, m, **kwargs) -> None:
        for name, value in kwargs.items():
            setattr(m, name, value)
        m.save()

    @classmethod
    def delete(cls, _id: int) -> None:
        m = cls.query.filter_by(id=_id).first()
        m.remove()

    @classmethod
    def all(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).all()
        return ms

    @classmethod
    def one(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).first()
        return ms

    @classmethod
    def order(cls, *args):
        ms = cls.query.order_by(*args).all()
        return ms

    @classmethod
    def get(cls, *args):
        ms = cls.query.get(*args)
        return ms

    @classmethod
    def count(cls) -> int:
        ms = cls.query.count()
        return ms

    @classmethod
    def offset(cls, *args):
        ms = cls.query.offset(*args).first()
        return ms

    @classmethod
    def page(cls, page: int, per_page: int, *args):
        ms = cls.query.order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms

    @classmethod
    def filter_page(cls, page: int, per_page: int, *args, **kwargs):
        ms = cls.query.filter_by(**kwargs).order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms
