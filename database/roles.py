from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from database import Base


class RolesORM(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key = True, index = True)
    category = Column(String(100), nullable = True)
    seniority = Column(String(50), nullable = True)
    show = Column(Boolean, nullable = False, default = False)
    featured = Column(Boolean, nullable = False, default = False)
    active = Column(Boolean, nullable = False, default = True)
    sort_order = Column(Integer, nullable = False, default = 0)
    color = Column(String(20), nullable = True)
    icon = Column(String(100), nullable = True)

    translations = relationship('RoleTranslationsORM', back_populates = 'role', cascade = 'all, delete-orphan', lazy = 'selectin')
