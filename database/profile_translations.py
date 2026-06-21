from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class ProfileTranslationsORM(Base):
    __tablename__ = 'profile_translations'
    __table_args__ = (UniqueConstraint('profile_id', 'locale', name = 'uq_profile_translations_profile_locale'),)

    id = Column(Integer, primary_key = True, index = True)
    profile_id = Column(Integer, ForeignKey('profile.id', ondelete = 'CASCADE'), nullable = False)
    locale = Column(String(2), nullable = False)
    summary = Column(Text, nullable = False, default = '')
    about_me = Column(Text, nullable = False, default = '')
    location = Column(String(150), nullable = False, default = '')

    profile = relationship('ProfileORM', back_populates = 'translations')
