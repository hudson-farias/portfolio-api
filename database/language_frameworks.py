from sqlalchemy import Column, ForeignKey, Integer

from database import Base


class LanguageFrameworksORM(Base):
    __tablename__ = 'language_frameworks'
    primary_key = 'language_id'

    language_id = Column(Integer, ForeignKey('languages.id', ondelete = 'CASCADE'), primary_key = True)
    framework_id = Column(Integer, ForeignKey('frameworks.id', ondelete = 'CASCADE'), primary_key = True)
