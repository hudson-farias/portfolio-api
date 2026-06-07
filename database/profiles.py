from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base


class ProfilesORM(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(150), nullable = False)
    last_name = Column(String(150), nullable = False, default = '')
    summary = Column(Text, nullable = False)
    about_me = Column(Text, nullable = False)
    location = Column(String(150), nullable = False, default = '')
    available = Column(Boolean, nullable = False, default = True)
