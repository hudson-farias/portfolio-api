from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from io import BytesIO

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


    def __add(self, text: str, style: str = 'Normal'):
        self.content.append(Paragraph(text, self.styles[style]))
        self.content.append(Spacer(1, 8))


    async def __header(self):
        self.__add('<b>Hudson Farias</b>', 'HeaderTitle')
        self.__add('Desenvolvedor de Software | Fullstack | DevOps', 'HeaderSubtitle')
        self.__add('Rio de Janeiro - Brasil | Português (Nativo) | Inglês (Técnico)')
        self.__add('<br />')


    async def __summary(self):
        self.__add('<b>Resumo Profissional</b>', 'SectionTitle')
        self.__add('Desenvolvedor de Software com experiência em desenvolvimento Fullstack, arquitetura de sistemas e práticas de DevOps. Atuação com APIs, microsserviços, automação e deploy em VPS. Experiência como Tech Leader em equipe pequena, com foco em performance, escalabilidade e segurança.')
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

        async with ExperiencesORM() as orm: experiences = await orm.find_many()

        for experience in experiences[::-1]:
            title = f'{experience.company} | {experience.role}' if experience.id != 3 else f'{experience.role}'
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
