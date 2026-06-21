from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class RoleTranslationsORM(Base):
    __tablename__ = 'role_translations'
    __table_args__ = (UniqueConstraint('role_id', 'locale', name = 'uq_role_translations_role_locale'),)

    id = Column(Integer, primary_key = True, index = True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete = 'CASCADE'), nullable = False)
    locale = Column(String(2), nullable = False)
    title = Column(String(150), nullable = False, default = '')
    summary = Column(Text, nullable = True)

    role = relationship('RolesORM', back_populates = 'translations')
