from database.skills_categories import SkillsCategoriesORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM
from database.social_networks import SocialNetworksORM
from database.profiles import ProfilesORM
from database.roles import RolesORM

from services.experiences import roles_map, role_title
from services.github import github

from models.landpage.about import AboutProfile, AboutResponse, Stats
from models.landpage.contact import ContactResponse
from models.landpage.experiences import Experience, ExperiencesResponse
from models.landpage.hero import HeroProfile, HeroResponse, SocialNetwork
from models.landpage.landpage import LandpageResponse
from models.landpage.projects import Project, ProjectsResponse
from models.landpage.skills import Skill, SkillCategory, SkillsResponse

from asyncio import gather


PROFILE = {
    'name': 'Hudson Farias',
    'roles': ['Software Developer', 'Fullstack Engineer', 'DevOps'],
    'location': 'Rio de Janeiro, Brasil',
    'email': 'hudson.farias.dev@gmail.com',
    'phone': '21 99688-9408',
    'about': 'Desenvolvedor de software com experiência desde janeiro de 2021. Construo aplicações web focadas em performance, qualidade e manutenção.',
    'about_extended': 'Atuo com desenvolvimento de software e tenho como base linguagens como Python, C#, TypeScript e PHP. Trabalho principalmente com FastAPI, Playwright, Next.js e Tailwind, unindo backend, frontend e automação para entregar produtos confiáveis. Experiência como Tech Leader em startup, liderando decisões técnicas, evolução arquitetural e otimizações de performance.',
    'available': True,
}

STATS = Stats(
    years_experience = 5,
    projects_count = 0,
    clients_count = 5,
)

class Landpage:
    async def __skills(self):
        data = []

        async with SkillsCategoriesORM() as orm: skills_categories = await orm.find_many()
        async with SkillsORM() as orm:
            for category in skills_categories:
                skills = await orm.find_many(skill_category_id = category.id)

                skill_data = SkillCategory(
                    title = category.title,
                    skills = [Skill(**skill.dict()) for skill in skills],
                )

                data.append(skill_data)

        return data


    async def __experiences(self):
        titles = await roles_map()

        async with ExperiencesORM() as orm:
            experiences = await orm.find_many(hidden = False)

        return [
            Experience(
                id = experience.id,
                company = experience.company,
                period = experience.period,
                role = role_title(experience.role_id, titles) or '',
                contract_type = experience.contract_type,
                description = experience.description,
            )
            for experience in experiences
        ]


    async def __visible_roles(self, locale: str = 'pt'):
        async with RolesORM() as orm:
            roles = await orm.find_many(show = True, active = True)

        roles = [role for role in roles if role.locale in (locale, 'todos')]
        roles.sort(key = lambda role: (not role.featured, role.sort_order, role.id))
        return [role.title for role in roles]


    async def __projects(self):
        async with ProjectsORM() as orm: projects = await orm.find_many()
        projects_ids = [project.git_id for project in projects]

        projects = github(True)

        data = []

        for project in projects:
            project_dto = Project(**project)
            project_dto.name = project_dto.name.replace('-', ' ').title()
            project_dto.html_url = None if project['private'] else project_dto.html_url

            if project['id'] in projects_ids: data.append(project_dto)

        return data


    async def __social_networks(self, show_header: bool = False, show_footer: bool = False):
        params = {
            'show_header': show_header,
            'show_footer': show_footer,
        }

        async with SocialNetworksORM() as orm: social_networks = await orm.find_many(**params)
        return [SocialNetwork(**social_network.dict()) for social_network in social_networks]


    async def __profile(self):
        async with ProfilesORM() as orm:
            return await orm.find_one()


    async def hero(self):
        profile = await self.__profile()
        visible_roles = await self.__visible_roles()

        return HeroResponse(
            profile = HeroProfile(
                name = profile.name if profile else PROFILE['name'].split()[0],
                roles = visible_roles if visible_roles else PROFILE['roles'],
                location = profile.location if profile else PROFILE['location'],
                email = PROFILE['email'],
                about = profile.summary if profile else PROFILE['about'],
                available = profile.available if profile else PROFILE['available'],
            ),
            social_networks = await self.__social_networks(show_header = True),
        )


    async def about(self):
        profile = await self.__profile()
        projects = await self.__projects()

        return AboutResponse(
            profile = AboutProfile(about_extended = profile.about_me if profile else PROFILE['about_extended']),
            stats = STATS.model_copy(update = {'projects_count': len(projects)}),
        )


    async def skills(self):
        return SkillsResponse(skills = await self.__skills())


    async def experiences(self):
        return ExperiencesResponse(experiences = await self.__experiences())


    async def projects(self):
        return ProjectsResponse(projects = await self.__projects())


    async def contact(self):
        return ContactResponse(
            email = PROFILE['email'],
            others = [],
        )


    async def all(self):
        about, contact, experiences, hero, projects, skills = await gather(
            self.about(),
            self.contact(),
            self.experiences(),
            self.hero(),
            self.projects(),
            self.skills(),
        )

        return LandpageResponse(
            about = about,
            contact = contact,
            experiences = experiences,
            hero = hero,
            projects = projects,
            skills = skills,
        )
