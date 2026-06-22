from sqlalchemy import Column, ForeignKey, Integer

from database import Base


class ProjectFrameworksORM(Base):
    __tablename__ = 'project_frameworks'
    primary_key = 'project_id'

    project_id = Column(Integer, ForeignKey('projects.id', ondelete = 'CASCADE'), primary_key = True)
    framework_id = Column(Integer, ForeignKey('frameworks.id', ondelete = 'CASCADE'), primary_key = True)
