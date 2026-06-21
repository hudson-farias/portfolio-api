from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ProjectsORM(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key = True, index = True)
    git_id = Column(Integer, nullable = False)
    image_url = Column(String(150), nullable = True)
    live_url = Column(String(150), nullable = True)
    repo_url = Column(String(150), nullable = True)

    translations = relationship('ProjectTranslationsORM', back_populates = 'project', cascade = 'all, delete-orphan', lazy = 'selectin')
