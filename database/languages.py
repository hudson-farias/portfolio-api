from sqlalchemy import Column, Integer, String

from database import Base


class LanguagesORM(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(255), nullable = False)
    icon = Column(String(100), nullable = False)
    sort_order = Column(Integer, nullable = False, default = 0)
