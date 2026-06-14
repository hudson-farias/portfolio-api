from sqlalchemy import Column, Integer, String

from database import Base


class DatabasesORM(Base):
    __tablename__ = 'databases'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(255), nullable = False)
    icon = Column(String(100), nullable = False)
    scope = Column(String(50), nullable = True)
    sort_order = Column(Integer, nullable = False, default = 0)
