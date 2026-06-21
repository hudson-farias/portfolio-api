from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class ExperienceTranslationsORM(Base):
    __tablename__ = 'experience_translations'
    __table_args__ = (UniqueConstraint('experience_id', 'locale', name = 'uq_experience_translations_experience_locale'),)

    id = Column(Integer, primary_key = True, index = True)
    experience_id = Column(Integer, ForeignKey('experiences.id', ondelete = 'CASCADE'), nullable = False)
    locale = Column(String(2), nullable = False)
    period = Column(String(100), nullable = False, default = '')
    description = Column(Text, nullable = False, default = '')

    experience = relationship('ExperiencesORM', back_populates = 'translations')
