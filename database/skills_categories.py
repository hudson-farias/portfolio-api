from sqlalchemy import Column, Integer, String
from database import Base

from database.skills import SkillsORM


class SkillsCategoriesORM(Base):
    __tablename__ = 'skills_categories'

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String(255), nullable = False)

    async def skills(self):
        async with SkillsORM() as orm: data = await orm.find_many(skill_category_id = self.id)
        return data
