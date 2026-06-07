from sqlalchemy import Column, Integer, String, Boolean, Text, UniqueConstraint
from database import Base


class RolesORM(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        UniqueConstraint('title', 'locale', name = 'uq_roles_title_locale'),
    )

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(150), nullable = False)
    summary = Column(Text, nullable = True)
    category = Column(String(100), nullable = True)
    seniority = Column(String(50), nullable = True)
    show = Column(Boolean, nullable = False, default = False)
    featured = Column(Boolean, nullable = False, default = False)
    locale = Column(String(10), nullable = False, default = 'pt')
    active = Column(Boolean, nullable = False, default = True)
    sort_order = Column(Integer, nullable = False, default = 0)
    color = Column(String(20), nullable = True)
    icon = Column(String(100), nullable = True)
