from typing import Optional

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from io import BytesIO

from sqlalchemy.orm import selectinload

from database.profile import ProfileORM
from database.roles import RolesORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.tools import ToolsORM
from database.frameworks import FrameworksORM
from database.databases import DatabasesORM
from database.languages import LanguagesORM
from database.language_frameworks import LanguageFrameworksORM

from services.resume_filters import database_matches_filter, experience_matches_filter, framework_matches_filter, skill_matches_filter, tool_matches_filter


class Curriculum:
    def __init__(self, filters: Optional[dict] = None):
        self.filters = filters or {}
        self.content = []
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(self.buffer)
        self.styles = getSampleStyleSheet()
        self.profile = None
        self.roles = None

        self.styles.add(ParagraphStyle(name = 'HeaderTitle', fontSize = 18, leading = 10))
        self.styles.add(ParagraphStyle(name = 'HeaderSubtitle', fontSize = 16, leading = 10))

        self.styles.add(ParagraphStyle(name = 'SectionTitle', fontSize = 14, leading = 14))
        self.styles.add(ParagraphStyle(name = 'SectionSubtitle', fontSize = 12, leading = 14))
        self.styles.add(ParagraphStyle(name = 'Body', fontSize = 10, leading = 12))


    def __add(self, text: str, style: str = 'Normal', spacer: int = 5):
        self.content.append(Paragraph(text, self.styles[style]))
        self.content.append(Spacer(1, spacer))


    async def __load_profile(self):
        if not self.profile:
            async with ProfileORM() as orm: self.profile = await orm.find_one()

        return self.profile


    async def __load_roles(self):
        if self.roles is None:
            async with RolesORM() as orm: rows = await orm.find_many(show = True, active = True)

            rows = [role for role in rows if role.locale is None or role.locale == 'pt']
            rows.sort(key = lambda role: (not role.featured, role.sort_order, role.id))
            self.roles = [role.title for role in rows]

        return self.roles


    def __full_name(self):
        profile = self.profile
        parts = [profile.name.strip(), profile.last_name.strip()]
        return ' '.join(part for part in parts if part)


    def __section_enabled(self, section: str):
        sections = self.filters.get('sections', set())
        if not sections: return True
        return section in sections


    async def __header(self):
        profile = await self.__load_profile()
        roles = await self.__load_roles()

        self.__add(f'<b>{self.__full_name()}</b>', 'HeaderTitle', spacer = 9)

        if roles: self.__add(' | '.join(roles), 'HeaderSubtitle', spacer = 9)

        if profile.location: self.__add(profile.location, spacer = 3)

        contact_parts = [part for part in [profile.email, profile.whatsapp] if part]
        if contact_parts: self.__add(' | '.join(contact_parts), spacer = 3)

        self.__add('<br />')


    async def __summary(self):
        profile = await self.__load_profile()
        if not profile.about_me: return

        self.__add('<b>Resumo Profissional</b>', 'SectionTitle')
        self.__add(profile.about_me.replace('\n', '<br />'))
        self.__add('<br />')


    async def __skills(self):
        sections = self.filters.get('sections', set())
        skill_ids = self.filters.get('skill_ids', set())
        has_skill_filter = bool(sections or skill_ids)

        async with SkillsORM() as orm: skills = await orm.find_many()
        if not skills: return

        if has_skill_filter:
            skills = [skill for skill in skills if skill_matches_filter(skill, sections, skill_ids)]
            if not skills: return

        skill_names = [skill.name for skill in skills]

        self.__add('<b>Habilidades</b>', 'SectionTitle')
        self.__add(', '.join(skill_names))
        self.__add('<br />')


    async def __frameworks(self):
        framework_ids = self.filters.get('framework_ids', set())
        language_ids = self.filters.get('language_ids', set())

        if not framework_ids and not language_ids and not self.__section_enabled('frameworks'): return

        async with FrameworksORM() as orm: framework_rows = await orm.find_many()
        if not framework_rows: return

        async with LanguagesORM() as orm: language_rows = await orm.find_many()
        languages_by_id = {row.id: row for row in language_rows}

        async with LanguageFrameworksORM() as orm: relations = await orm.find_many()
        languages_by_framework = {}

        for relation in relations:
            languages_by_framework.setdefault(relation.framework_id, []).append(relation.language_id)

        framework_rows.sort(key = lambda framework: (framework.sort_order, framework.id))

        scope_labels = {
            'backend': 'Backend',
            'frontend': 'Frontend',
        }
        grouped = {}

        for framework in framework_rows:
            linked_language_ids = set(languages_by_framework.get(framework.id, []))

            if not framework_matches_filter(framework.id, linked_language_ids, framework_ids, language_ids):
                continue

            linked = [
                languages_by_id[language_id].name
                for language_id in linked_language_ids
                if language_id in languages_by_id
            ]
            linked.sort(key = lambda name: name.lower())

            label = framework.name
            if linked:
                label = f'{framework.name} ({", ".join(linked)})'

            scope_key = framework.scope or 'outros'
            grouped.setdefault(scope_key, []).append(label)

        if not grouped: return

        self.__add('<b>Frameworks</b>', 'SectionTitle')

        for scope_key in ('backend', 'frontend', 'outros'):
            items = grouped.get(scope_key)
            if not items: continue

            title = scope_labels.get(scope_key, 'Outros')
            self.__add(f'<b>{title}</b>: {", ".join(items)}')

        self.__add('<br />')


    async def __databases(self):
        database_ids = self.filters.get('database_ids', set())
        sections = self.filters.get('sections', set())

        if not database_ids and sections and 'databases' not in sections: return

        async with DatabasesORM() as orm: database_rows = await orm.find_many()
        if not database_rows: return

        database_rows.sort(key = lambda database: (database.sort_order, database.id))

        scope_labels = {
            'sql': 'SQL',
            'nosql': 'NoSQL',
        }
        grouped = {}

        for database in database_rows:
            if not database_matches_filter(database.id, database_ids, sections): continue

            scope_key = database.scope or 'outros'
            grouped.setdefault(scope_key, []).append(database.name)

        if not grouped: return

        self.__add('<b>Banco de dados</b>', 'SectionTitle')

        for scope_key in ('sql', 'nosql', 'outros'):
            items = grouped.get(scope_key)
            if not items: continue

            title = scope_labels.get(scope_key, 'Outros')
            self.__add(f'<b>{title}</b>: {", ".join(items)}')

        self.__add('<br />')


    async def __tools(self):
        tool_ids = self.filters.get('tool_ids', set())
        if not self.filters.get('include_tools') and not tool_ids: return

        async with ToolsORM() as orm: tools = await orm.find_many()
        tools.sort(key = lambda tool: (tool.sort_order, tool.id))

        if tool_ids:
            tools = [tool for tool in tools if tool_matches_filter(tool.id, tool_ids)]

        if not tools: return

        self.__add('<b>Ferramentas</b>', 'SectionTitle')
        self.__add(', '.join(tool.name for tool in tools))
        self.__add('<br />')


    async def __experience(self):
        experience_ids = self.filters.get('experience_ids', set())

        async with ExperiencesORM() as orm:
            experiences = await orm.find_many(hidden = False, options = selectinload(ExperiencesORM.role))

        visible = [experience for experience in experiences[::-1] if experience_matches_filter(experience.id, experience_ids)]
        if not visible: return

        self.__add('<b>Experiência Profissional</b>', 'SectionTitle')

        for experience in visible:
            title = f'{experience.company} | {experience.role_title or ""}'
            self.__add(f'<b>{title} | {experience.period} </b>', 'SectionSubtitle')
            self.__add(experience.description.replace('\n', '<br />'))

        self.__add('<br />')


    async def __education(self):
        self.__add('<b>Formação Acadêmica</b>', 'SectionTitle')
        self.__add('<b>Uniasselvi - Análise e Desenvolvimento de Sistemas (ADS) | 2026 - 2028</b>', 'SectionSubtitle')


    async def generate(self):
        await self.__header()
        await self.__summary()
        await self.__skills()
        await self.__frameworks()
        await self.__databases()
        await self.__tools()
        await self.__experience()
        await self.__education()

        self.doc.build(self.content)

        self.buffer.seek(0)

        return self.buffer
