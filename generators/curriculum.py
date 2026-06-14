from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from io import BytesIO

from sqlalchemy.orm import selectinload

from database.skills_categories import SkillsCategoriesORM
from database.experiences import ExperiencesORM

class Curriculum:
    def __init__(self):
        self.content = []
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(self.buffer)
        self.styles = getSampleStyleSheet()

        self.styles.add(ParagraphStyle(name = 'HeaderTitle', fontSize = 18, leading = 10))
        self.styles.add(ParagraphStyle(name = 'HeaderSubtitle', fontSize = 16, leading = 10))

        self.styles.add(ParagraphStyle(name = 'SectionTitle', fontSize = 14, leading = 14))
        self.styles.add(ParagraphStyle(name = 'SectionSubtitle', fontSize = 12, leading = 14))
        self.styles.add(ParagraphStyle(name = 'Body', fontSize = 10, leading = 12))


    def __add(self, text: str, style: str = 'Normal', spacer: int = 5):
        self.content.append(Paragraph(text, self.styles[style]))
        self.content.append(Spacer(1, spacer))


    async def __header(self):
        self.__add('<b>Hudson Farias</b>', 'HeaderTitle', spacer = 9)
        self.__add('Software Engineer | Fullstack Engineer | DevOps', 'HeaderSubtitle', spacer = 9)
        self.__add('Rio de Janeiro - Brasil | Português (Nativo) | Inglês (Técnico)', spacer = 3)
        self.__add('hudson.farias.dev@gmail.com | 21 99688-9408', spacer = 3)
        self.__add('<br />')


    async def __summary(self):
        self.__add('<b>Resumo Profissional</b>', 'SectionTitle')
        self.__add('Software Engineer com experiência em desenvolvimento backend, arquitetura de sistemas e práticas DevOps. Atuação em aplicações Fullstack com FastAPI, Next.js e TypeScript, incluindo microsserviços, automações, integrações e deploy em VPS Linux com Docker e Nginx. \n\n Experiência como Tech Leader em startup, liderando decisões técnicas, evolução arquitetural, manutenção de sistemas legados e otimizações de performance.')
        self.__add('<br />')


    async def __skills(self):
        self.__add('<b>Habilidades</b>', 'SectionTitle')

        async with SkillsCategoriesORM() as orm: skills_cat = await orm.find_many()
        for cat in skills_cat:
            skills = await cat.skills()
            if not skills: continue

            skills = [skill.name for skill in skills]
            self.__add(f'<b>{cat.title}</b>: {', '.join(skills)}')

        self.__add('<br />')


    async def __experience(self):
        self.__add('<b>Experiência Profissional</b>', 'SectionTitle')

        async with ExperiencesORM() as orm:
            experiences = await orm.find_many(hidden = False, options = selectinload(ExperiencesORM.role))

        for experience in experiences[::-1]:
            title = f'{experience.company} | {experience.role_title or ""}'
            # title = f'{experience.company} | {experience.role}' if experience.id != 3 else f'{experience.role}'
            self.__add(f'<b>{title} | {experience.period} </b>', 'SectionSubtitle')
            self.__add(experience.description)

        self.__add('<br />')


    async def __education(self):
        self.__add('<b>Formação Acadêmica</b>', 'SectionTitle')
        self.__add('<b>Uniasselvi - Análise e Desenvolvimento de Sistemas (ADS) | 2026 - 2028</b>', 'SectionSubtitle')


    async def generate(self):
        await self.__header()
        await self.__summary()
        await self.__skills()
        await self.__experience()
        await self.__education()

        self.doc.build(self.content)

        self.buffer.seek(0)

        return self.buffer
