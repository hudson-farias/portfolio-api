from database.social_networks import SocialNetworksORM
from database.tools import ToolsORM
from database.languages import LanguagesORM
from database.frameworks import FrameworksORM
from database.databases import DatabasesORM
from database.language_frameworks import LanguageFrameworksORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM
from database.profile import ProfileORM
from database.roles import RolesORM

from services.github import github

from models.landpage import *

from models.landpage.frameworks import Framework as LandpageFramework, LandpageLanguageRef, FrameworksResponse
from models.landpage.databases import Database as LandpageDatabase, DatabasesResponse

from asyncio import gather
from datetime import datetime


class Landpage:
    def __init__(self, locale: str = 'pt'):
        self.__locale = locale if locale in ('pt', 'en') else 'pt'
        self.__skills = None
        self.__experiences = None
        self.__role_titles = None
        self.__projects = None
        self.__profile = None
        self.__social_networks = None
        self.__tools = None
        self.__frameworks = None
        self.__databases = None


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
            async with SkillsORM() as orm: skills = await orm.find_many()
            self.__skills = [Skill(**skill.dict()) for skill in skills]

        return self.__skills


    async def __fetch_experiences(self):
        if not self.__experiences:
            async with ExperiencesORM() as orm:
                experiences = await orm.find_many(hidden = False)

            self.__experiences = []

            for experience in experiences:
                picked = [t for t in experience.translations if t.locale == self.__locale]
                if not picked:
                    picked = [t for t in experience.translations if t.locale == 'pt']
                translation = picked[0] if picked else None

                role_translation = None
                if experience.role:
                    role_picked = [t for t in experience.role.translations if t.locale == self.__locale]
                    if not role_picked:
                        role_picked = [t for t in experience.role.translations if t.locale == 'pt']
                    role_translation = role_picked[0] if role_picked else None

                self.__experiences.append(Experience(
                    id = experience.id,
                    company = experience.company,
                    period = translation.period or '' if translation else '',
                    role = role_translation.title or '' if role_translation else '',
                    contract_type = experience.contract_type,
                    description = translation.description or '' if translation else '',
                    live_url = experience.live_url,
                ))

        return self.__experiences


    async def __fetch_roles(self):
        if self.__role_titles is None:
            async with RolesORM() as orm:
                roles = await orm.find_many(show = True, active = True)
            roles.sort(key = lambda role: (not role.featured, role.sort_order, role.id))

            self.__role_titles = []
            for role in roles:
                picked = [t for t in role.translations if t.locale == self.__locale]
                if not picked:
                    picked = [t for t in role.translations if t.locale == 'pt']
                translation = picked[0] if picked else None
                self.__role_titles.append(translation.title or '' if translation else '')

        return self.__role_titles


    async def __fetch_projects(self):
        if not self.__projects:
            async with ProjectsORM() as orm:
                projects_db = await orm.find_many()

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
                picked = [t for t in db.translations if t.locale == self.__locale]
                if not picked:
                    picked = [t for t in db.translations if t.locale == 'pt']
                translation = picked[0] if picked else None

                self.__projects.append(Project(
                    id = git_id,
                    name = translation.title or gh_name if translation else gh_name,
                    description = translation.description or gh_description if translation else gh_description,
                    image_url = db.image_url,
                    homepage = db.live_url or project.get('homepage') or None,
                    html_url = db.repo_url or (None if project.get('private') else project.get('html_url')),
                ))

            for db in projects_db:
                if db.git_id >= 0: continue

                picked = [t for t in db.translations if t.locale == self.__locale]
                if not picked:
                    picked = [t for t in db.translations if t.locale == 'pt']
                translation = picked[0] if picked else None

                self.__projects.append(Project(
                    id = db.git_id,
                    name = translation.title or 'Projeto externo' if translation else 'Projeto externo',
                    description = translation.description or '' if translation else '',
                    image_url = db.image_url,
                    homepage = db.live_url,
                    html_url = db.repo_url,
                ))

        return self.__projects


    async def __fetch_profile(self):
        if not self.__profile:
            async with ProfileORM() as orm:
                self.__profile = await orm.find_one()

        return self.__profile


    async def hero(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()
        visible_roles = await self.__fetch_roles()
        picked = [t for t in profile.translations if t.locale == self.__locale]
        if not picked:
            picked = [t for t in profile.translations if t.locale == 'pt']
        translation = picked[0] if picked else None

        return HeroResponse(
            profile = HeroProfile(
                name = profile.name,
                roles = visible_roles,
                location = translation.location or '' if translation else '',
                email = profile.email,
                about = translation.summary or '' if translation else '',
                available = profile.available,
            ),
            social_networks = self.__social_networks.get('hero') or []
        )


    async def about(self):
        await self.__fetch_social_networks()
        profile = await self.__fetch_profile()
        projects = await self.__fetch_projects()
        years_experience = max(0, datetime.now().year - profile.career_start)
        picked = [t for t in profile.translations if t.locale == self.__locale]
        if not picked:
            picked = [t for t in profile.translations if t.locale == 'pt']
        translation = picked[0] if picked else None

        return AboutResponse(
            profile = AboutProfile(about_extended = translation.about_me or '' if translation else ''),
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


    async def __fetch_tools(self):
        if not self.__tools:
            async with ToolsORM() as orm: rows = await orm.find_many()
            rows.sort(key = lambda tool: (tool.sort_order, tool.id))
            self.__tools = [Tool(**row.dict()) for row in rows]

        return self.__tools


    async def tools(self):
        return ToolsResponse(tools = await self.__fetch_tools())


    async def __fetch_relations(self):
        async with LanguageFrameworksORM() as orm: relations = await orm.find_many()

        by_framework = {}
        by_language = {}

        for relation in relations:
            by_framework.setdefault(relation.framework_id, []).append(relation.language_id)
            by_language.setdefault(relation.language_id, []).append(relation.framework_id)

        return by_framework, by_language


    async def __fetch_frameworks(self):
        if not self.__frameworks:
            async with FrameworksORM() as orm: rows = await orm.find_many()
            rows.sort(key = lambda framework: (framework.sort_order, framework.id))

            async with LanguagesORM() as orm: language_rows = await orm.find_many()
            languages_by_id = {row.id: row for row in language_rows}

            by_framework, by_language = await self.__fetch_relations()
            self.__frameworks = []

            for row in rows:
                linked = [
                    LandpageLanguageRef(
                        id = language_rows.id,
                        name = language_rows.name,
                        icon = language_rows.icon,
                    )
                    for language_id in by_framework.get(row.id, [])
                    if (language_rows := languages_by_id.get(language_id))
                ]
                linked.sort(key = lambda item: item.name.lower())
                self.__frameworks.append(LandpageFramework(**row.dict(), languages = linked))

        return self.__frameworks


    async def frameworks(self):
        return FrameworksResponse(frameworks = await self.__fetch_frameworks())


    async def __fetch_databases(self):
        if not self.__databases:
            async with DatabasesORM() as orm: rows = await orm.find_many()
            rows.sort(key = lambda database: (database.sort_order, database.id))
            self.__databases = [LandpageDatabase(**row.dict()) for row in rows]

        return self.__databases


    async def databases(self):
        return DatabasesResponse(databases = await self.__fetch_databases())


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
        picked = [t for t in profile.translations if t.locale == self.__locale]
        if not picked:
            picked = [t for t in profile.translations if t.locale == 'pt']
        translation = picked[0] if picked else None

        return MetadataResponse(
            name = profile.name,
            roles = visible_roles,
            about = translation.summary or '' if translation else '',
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

        about, contact, experiences, hero, projects, skills, tools = await gather(
            self.about(),
            self.contact(),
            self.experiences(),
            self.hero(),
            self.projects(),
            self.skills(),
            self.tools(),
        )

        return PageResponse(
            about = about,
            contact = contact,
            experiences = experiences,
            hero = hero,
            projects = projects,
            skills = skills,
            tools = tools,
        )
