from database.social_networks import SocialNetworksORM
from database.skills_categories import SkillsCategoriesORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM
from database.profiles import ProfilesORM
from database.roles import RolesORM

from services.experiences import roles_map, role_title
from services.github import github

from models.landpage import *

from asyncio import gather


STATS = Stats(
    years_experience = 5,
    projects_count = 0,
    clients_count = 5,
)

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
            async with ProjectsORM() as orm: projects = await orm.find_many()
            projects_ids = [project.git_id for project in projects]

            projects = github(True)

            self.__projects = []

            for project in projects:
                project_dto = Project(**project)
                project_dto.name = project_dto.name.replace('-', ' ').title()
                project_dto.html_url = None if project['private'] else project_dto.html_url

                if project['id'] in projects_ids: self.__projects.append(project_dto)

        return self.__projects


    async def __fetch_profile(self):
        if not self.__profile:
            async with ProfilesORM() as orm: self.__profile = await orm.find_one()

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
                about = profile.summary,
                available = profile.available,
            ),
            social_networks = self.__social_networks.get('hero') or []
        )


    async def about(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()
        projects = await self.__fetch_projects()
        experiences = await self.__fetch_experiences()
        companies_count = len({experience.company for experience in experiences})

        return AboutResponse(
            profile = AboutProfile(about_extended = profile.about_me),
            stats = STATS.model_copy(update = {
                'projects_count': len(projects),
                'clients_count': companies_count or STATS.clients_count,
            }),
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

        hero, contact = await gather(self.hero(), self.contact())

        return LayoutResponse(
            hero = hero,
            footer = FooterResponse(social_networks = self.__social_networks.get('footer') or []),
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
