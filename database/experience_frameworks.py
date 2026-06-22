from sqlalchemy import Column, ForeignKey, Integer

from database import Base


class ExperienceFrameworksORM(Base):
    __tablename__ = 'experience_frameworks'
    primary_key = 'experience_id'

    experience_id = Column(Integer, ForeignKey('experiences.id', ondelete = 'CASCADE'), primary_key = True)
    framework_id = Column(Integer, ForeignKey('frameworks.id', ondelete = 'CASCADE'), primary_key = True)
