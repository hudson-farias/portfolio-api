from database.social_networks import SocialNetworksORM
from database.skills_categories import SkillsCategoriesORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM
from database.profile import ProfileORM
from database.roles import RolesORM

from services.experiences import roles_map, role_title
from services.github import github

from models.landpage import *

from asyncio import gather
from datetime import datetime


class Landpage:
    __skills = None
    __experiences = None
    __roles = None
    __projects = None
    __profile = None
    __social_networks = None


    async def __fetch_social_networks(self):
        if not self.__social_networks:
            self.__social_networks = {}

            async with SocialNetworksORM() as orm: rows = await orm.find_many()

            for item in rows:
                network = SocialNetwork(**item.dict())

                for section in item.positions:
                    if section not in self.__social_networks: self.__social_networks[section] = []
                    self.__social_networks[section].append(network)

        return self.__social_networks


    async def __fetch_skills(self):
        if not self.__skills:
            self.__skills = []

            async with SkillsCategoriesORM() as orm: skills_categories = await orm.find_many()
            async with SkillsORM() as orm:
                for category in skills_categories:
                    skills = await orm.find_many(skill_category_id = category.id)
                    skill_data = SkillCategory(title = category.title, skills = [Skill(**skill.dict()) for skill in skills],)

                    self.__skills.append(skill_data)

        return self.__skills


    async def __fetch_experiences(self):
        if not self.__experiences:
            titles = await roles_map()

            async with ExperiencesORM() as orm: experiences = await orm.find_many(hidden = False)

            self.__experiences = [Experience(
                id = experience.id,
                company = experience.company,
                period = experience.period,
                role = role_title(experience.role_id, titles) or '',
                contract_type = experience.contract_type,
                description = experience.description,
            ) for experience in experiences]

        return self.__experiences


    async def __fetch_roles(self, locale: str = 'pt'):
        if not self.__roles:
            async with RolesORM() as orm:
                roles = await orm.find_many(show = True, active = True)

            roles = [role for role in roles if role.locale is None or role.locale == locale]
            roles.sort(key = lambda role: (not role.featured, role.sort_order, role.id))

            self.__roles = [role.title for role in roles]

        return self.__roles


    async def __fetch_projects(self):
        if not self.__projects:
            async with ProjectsORM() as orm: projects_db = await orm.find_many()
            projects_mapper = {project.git_id: project for project in projects_db}
            projects_ids = set(projects_mapper.keys())

            projects = github(True)

            self.__projects = []

            for project in projects:
                git_id = project['id']
                if git_id not in projects_ids: continue

                db = projects_mapper[git_id]
                gh_name = project['name'].replace('-', ' ').title()
                gh_description = project.get('description') or ''

                self.__projects.append(Project(
                    id = git_id,
                    name = db.title or gh_name,
                    description = db.description or gh_description,
                    image_url = db.image_url,
                    homepage = db.live_url or project.get('homepage') or None,
                    html_url = db.repo_url or (None if project.get('private') else project.get('html_url')),
                ))

            for db in projects_db:
                if db.git_id >= 0: continue

                self.__projects.append(Project(
                    id = db.git_id,
                    name = db.title or 'Projeto externo',
                    description = db.description or '',
                    image_url = db.image_url,
                    homepage = db.live_url,
                    html_url = db.repo_url,
                ))

        return self.__projects


    async def __fetch_profile(self):
        if not self.__profile:
            async with ProfileORM() as orm: self.__profile = await orm.find_one()

        return self.__profile


    async def hero(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()
        visible_roles = await self.__fetch_roles()

        return HeroResponse(
            profile = HeroProfile(
                name = profile.name,
                roles = visible_roles,
                location = profile.location,
                email = profile.email,
                about = profile.summary,
                available = profile.available,
            ),
            social_networks = self.__social_networks.get('hero') or []
        )


    async def about(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()
        projects = await self.__fetch_projects()
        years_experience = max(0, datetime.now().year - profile.career_start)

        return AboutResponse(
            profile = AboutProfile(about_extended = profile.about_me),
            stats = Stats(
                years_experience = years_experience,
                projects_count = len(projects),
            ),
            linkedin = profile.linkedin,
            social_networks = self.__social_networks.get('about') or [],
            profile_name = profile.name,
        )


    async def skills(self):
        return SkillsResponse(skills = await self.__fetch_skills())


    async def experiences(self):
        return ExperiencesResponse(experiences = await self.__fetch_experiences())


    async def projects(self):
        return ProjectsResponse(projects = await self.__fetch_projects())


    async def contact(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()

        return ContactResponse(
            email = profile.email,
            whatsapp_url = profile.whatsapp_url,
            linkedin = profile.linkedin,
            github = profile.github,
            gitlab = profile.gitlab,
            others = self.__social_networks.get('contact') or [],
            profile_name = profile.name,
        )


    async def metadata(self):
        profile = await self.__fetch_profile()
        visible_roles = await self.__fetch_roles()

        return MetadataResponse(
            name = profile.name,
            roles = visible_roles,
            about = profile.summary,
        )


    async def layout(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()

        hero, contact = await gather(self.hero(), self.contact())

        return LayoutResponse(
            hero = hero,
            footer = FooterResponse(
                github = profile.github,
                gitlab = profile.gitlab,
                linkedin = profile.linkedin,
                career_start = profile.career_start,
                social_networks = self.__social_networks.get('footer') or [],
            ),
            contact = contact,
        )


    async def page(self):
        await self.__fetch_social_networks()

        about, contact, experiences, hero, projects, skills = await gather(
            self.about(),
            self.contact(),
            self.experiences(),
            self.hero(),
            self.projects(),
            self.skills(),
        )

        return PageResponse(
            about = about,
            contact = contact,
            experiences = experiences,
            hero = hero,
            projects = projects,
            skills = skills,
        )
