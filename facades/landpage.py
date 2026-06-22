from database.social_networks import SocialNetworksORM
from database.tools import ToolsORM
from database.languages import LanguagesORM
from database.frameworks import FrameworksORM
from database.databases import DatabasesORM
from database.language_frameworks import LanguageFrameworksORM
from database.experience_frameworks import ExperienceFrameworksORM
from database.project_frameworks import ProjectFrameworksORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM
from database.profile import ProfileORM
from database.roles import RolesORM

from services.github import github

from models.landpage import *

from models.landpage.frameworks import Framework as LandpageFramework, LandpageFrameworkRef, LandpageLanguageRef, FrameworksResponse
from models.landpage.databases import Database as LandpageDatabase, DatabasesResponse

from asyncio import Lock, gather
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
        self.__frameworks_by_id = None
        self.__languages_by_framework = None
        self.__experience_framework_ids = None
        self.__project_framework_ids = None
        self.__projects_lock = Lock()


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


    async def __fetch_experience_framework_ids(self):
        if self.__experience_framework_ids is None:
            async with ExperienceFrameworksORM() as orm: relations = await orm.find_many()

            self.__experience_framework_ids = {}

            for relation in relations:
                self.__experience_framework_ids.setdefault(relation.experience_id, []).append(relation.framework_id)

        return self.__experience_framework_ids


    async def __fetch_project_framework_ids(self):
        if self.__project_framework_ids is None:
            async with ProjectFrameworksORM() as orm: relations = await orm.find_many()

            self.__project_framework_ids = {}

            for relation in relations:
                self.__project_framework_ids.setdefault(relation.project_id, []).append(relation.framework_id)

        return self.__project_framework_ids


    async def __ensure_framework_lookup(self):
        await self.__fetch_frameworks()

        if self.__frameworks_by_id is None:
            self.__frameworks_by_id = {framework.id: framework for framework in self.__frameworks}

        if self.__languages_by_framework is None:
            by_framework, by_language = await self.__fetch_relations()
            self.__languages_by_framework = by_framework

        return self.__frameworks_by_id, self.__languages_by_framework


    async def __framework_refs(self, framework_ids):
        if not framework_ids: return []

        frameworks_by_id, languages_by_framework = await self.__ensure_framework_lookup()
        async with LanguagesORM() as orm: language_rows = await orm.find_many()
        languages_by_id = {row.id: row for row in language_rows}

        refs = []

        for framework_id in framework_ids:
            framework = frameworks_by_id.get(framework_id)
            if not framework: continue

            linked = [
                LandpageLanguageRef(
                    id = language_row.id,
                    name = language_row.name,
                    icon = language_row.icon,
                )
                for language_id in languages_by_framework.get(framework_id, [])
                if (language_row := languages_by_id.get(language_id))
            ]
            linked.sort(key = lambda item: item.name.lower())

            refs.append(LandpageFrameworkRef(
                id = framework.id,
                name = framework.name,
                icon = framework.icon,
                languages = linked,
            ))

        refs.sort(key = lambda item: (item.name.lower(), item.id))
        return refs


    async def __fetch_experiences(self):
        if not self.__experiences:
            async with ExperiencesORM() as orm:
                experiences = await orm.find_many(hidden = False)

            experience_framework_ids = await self.__fetch_experience_framework_ids()
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

                framework_ids = experience_framework_ids.get(experience.id, [])
                frameworks = await self.__framework_refs(framework_ids)

                self.__experiences.append(Experience(
                    id = experience.id,
                    company = experience.company,
                    period = translation.period or '' if translation else '',
                    role = role_translation.title or '' if role_translation else '',
                    contract_type = experience.contract_type,
                    description = translation.description or '' if translation else '',
                    live_url = experience.live_url,
                    frameworks = frameworks,
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


    def __project_dedupe_key(self, git_id: int, html_url, homepage):
        url = (html_url or homepage or '').strip().rstrip('/').lower()
        if url: return url
        return f'git:{git_id}'


    async def __fetch_projects(self):
        if self.__projects is not None:
            return self.__projects

        async with self.__projects_lock:
            if self.__projects is not None:
                return self.__projects

            async with ProjectsORM() as orm:
                projects_db = await orm.find_many()

            github_by_id = {project['id']: project for project in github(True)}
            project_framework_ids = await self.__fetch_project_framework_ids()

            items = []
            seen_git_ids = set()
            seen_repo_keys = set()

            for db in sorted(projects_db, key = lambda row: row.id):
                if db.git_id > 0 and db.git_id in seen_git_ids:
                    continue

                picked = [t for t in db.translations if t.locale == self.__locale]
                if not picked:
                    picked = [t for t in db.translations if t.locale == 'pt']
                translation = picked[0] if picked else None

                frameworks = await self.__framework_refs(project_framework_ids.get(db.id, []))

                if db.git_id > 0:
                    gh = github_by_id.get(db.git_id)
                    if not gh: continue

                    gh_name = gh['name'].replace('-', ' ').title()
                    gh_description = gh.get('description') or ''
                    html_url = db.repo_url or (None if gh.get('private') else gh.get('html_url'))
                    homepage = db.live_url or gh.get('homepage') or None
                    name = translation.title or gh_name if translation else gh_name
                    description = translation.description or gh_description if translation else gh_description
                    project_id = db.git_id
                    seen_git_ids.add(db.git_id)
                else:
                    html_url = db.repo_url
                    homepage = db.live_url
                    name = translation.title or 'Projeto externo' if translation else 'Projeto externo'
                    description = translation.description or '' if translation else ''
                    project_id = db.git_id

                repo_key = self.__project_dedupe_key(project_id, html_url, homepage)
                if repo_key in seen_repo_keys:
                    continue
                seen_repo_keys.add(repo_key)

                items.append(Project(
                    id = project_id,
                    name = name,
                    description = description,
                    image_url = db.image_url,
                    homepage = homepage,
                    html_url = html_url,
                    frameworks = frameworks,
                ))

            self.__projects = items
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
