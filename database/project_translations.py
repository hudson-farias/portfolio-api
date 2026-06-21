from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class ProjectTranslationsORM(Base):
    __tablename__ = 'project_translations'
    __table_args__ = (UniqueConstraint('project_id', 'locale', name = 'uq_project_translations_project_locale'),)

    id = Column(Integer, primary_key = True, index = True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete = 'CASCADE'), nullable = False)
    locale = Column(String(2), nullable = False)
    title = Column(String(255), nullable = False, default = '')
    description = Column(Text, nullable = True)

    project = relationship('ProjectsORM', back_populates = 'translations')
