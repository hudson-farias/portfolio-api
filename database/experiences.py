from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class ExperiencesORM(Base):
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key = True, index = True)
    company = Column(String(255), nullable = False)
    period = Column(String(100), nullable = False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete = 'SET NULL'), nullable = True)
    contract_type = Column(String(20), nullable = True)
    description = Column(String(255), nullable = False)
    hidden = Column(Boolean, nullable = False, default = False)

    role = relationship('RolesORM', foreign_keys = [role_id])

    @property
    def role_title(self):
        if self.role is None: return None
        return self.role.title
