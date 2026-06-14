from re import sub

from sqlalchemy import Column, Integer, String, Text, Boolean

from database import Base


class ProfileORM(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(150), nullable = False)
    last_name = Column(String(150), nullable = False, default = '')
    summary = Column(Text, nullable = False)
    about_me = Column(Text, nullable = False)
    location = Column(String(150), nullable = False, default = '')
    available = Column(Boolean, nullable = False, default = True)
    email = Column(String(255), nullable = False)
    whatsapp = Column(String(30), nullable = False)
    linkedin = Column(String(200), nullable = False)
    github = Column(String(200), nullable = False)
    gitlab = Column(String(200), nullable = False)

    @property
    def whatsapp_url(self):
        digits = sub(r'\D', '', self.whatsapp)
        return f'https://wa.me/{digits}'
