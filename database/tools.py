from sqlalchemy import Column, Integer, String

from database import Base


class ToolsORM(Base):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(255), nullable = False)
    icon = Column(String(100), nullable = False)
    url = Column(String(255), nullable = True)
    sort_order = Column(Integer, nullable = False, default = 0)
