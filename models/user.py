from sqlalchemy import Column, String
from models import BaseModel, db


class User(BaseModel, db.Model):
    username = Column(String(50), nullable=False)
    password = Column(String(256), nullable=False)
