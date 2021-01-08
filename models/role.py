from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from models import BaseModel
from models.extensions import db


class Permission:
    COMMENT = 1
    DELETE = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(BaseModel, db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [
                Permission.DELETE,
                Permission.COMMENT,
                Permission.WRITE
            ],
            'Moderator': [
                Permission.DELETE,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE
            ],
            'Administrator': [
                Permission.DELETE,
                Permission.COMMENT,
                Permission.WRITE,
                Permission.MODERATE,
                Permission.ADMIN
            ],
        }
        default_role = 'User'
        for r in roles:
            role = Role.one(name=r)
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            role.save()

    def has_permission(self, perm: int) -> bool:
        return self.permissions & perm == perm

    def reset_permissions(self) -> None:
        self.permissions = 0

    def add_permission(self, perm: int) -> None:
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm: int) -> None:
        if self.has_permission(perm):
            self.permissions -= perm

    def users_page(self, page: int, per_page: int, *args):
        ms = self.users.order_by(*args).paginate(
            page, per_page=per_page, error_out=False
        )
        return ms
