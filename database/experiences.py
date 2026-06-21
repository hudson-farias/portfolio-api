from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class ExperiencesORM(Base):
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key = True, index = True)
    company = Column(String(255), nullable = False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete = 'SET NULL'), nullable = True)
    contract_type = Column(String(20), nullable = True)
    live_url = Column(String(150), nullable = True)
    hidden = Column(Boolean, nullable = False, default = False)

    role = relationship('RolesORM', foreign_keys = [role_id], lazy = 'selectin')
    translations = relationship('ExperienceTranslationsORM', back_populates = 'experience', cascade = 'all, delete-orphan', lazy = 'selectin')
