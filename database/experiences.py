from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class ExperiencesORM(Base):
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key = True, index = True)
    company = Column(String(255), nullable = False)
    period = Column(String(100), nullable = False)
    role = Column(String(150), nullable = False)
    description = Column(String(255), nullable = False)
    hidden = Column(Boolean, nullable = False, default = False)
