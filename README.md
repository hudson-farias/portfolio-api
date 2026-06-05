# Portfolio API

Backend que alimenta meu portfólio. Centralizo aqui perfil, experiências, habilidades, projetos e redes sociais em uma API REST — separando conteúdo da apresentação visual para poder atualizar o site sem mexer no frontend.

## O que é

Construí uma API em FastAPI que atende dois públicos: visitantes da landing page, que recebem apenas dados públicos; e eu, que gerencio tudo por um painel admin com autenticação restrita.

O conteúdo vive no PostgreSQL. Sincronizo projetos com o GitHub — só entram no portfólio os repositórios que escolho manualmente. Repositórios privados ficam ocultos para quem não está autenticado.

## Endpoints públicos

Rotas que alimentam o site, sem necessidade de login:

- **Hero** — meu nome, cargos, localização, disponibilidade e redes do header
- **About** — texto estendido e estatísticas da minha carreira
- **Skills** — categorias e habilidades que cadastrei
- **Experiences** — meu histórico profissional (registros não ocultos)
- **Projects** — repositórios públicos que selecionei no GitHub
- **Contact** — meu e-mail e canais de contato
- **Curriculum** — geração de PDF do meu currículo a partir dos dados do banco

## Painel admin

Área protegida onde só eu (ou quem autorizei) pode editar:

- **Dashboard** — visão geral com contadores e prévias de cada seção
- **Experiências** — crio, edito, oculto e removo registros
- **Skills** — gerencio categorias e habilidades com ícones
- **Projetos** — escolho quais repositórios do GitHub aparecem no site
- **Redes sociais** — configuro os links exibidos no header e no footer

Visitantes não autenticados ainda podem acessar o dashboard em modo leitura, mas veem apenas dados públicos — sem projetos privados nem experiências ocultas.

## Autenticação

Implementei login via **OAuth do Discord**. Apenas e-mails que autorizei recebem um JWT para editar conteúdo. Valido tokens em cada requisição sensível; sem credencial válida, a API responde apenas com o que é público.

## Integrações

| Serviço | Como uso |
|---------|----------|
| **GitHub** | Listo meus repositórios (públicos ou privados, conforme autenticação) e exponho nome, descrição, URL e homepage |
| **Discord** | Fluxo OAuth para me identificar como dono do portfólio |
| **PostgreSQL** | Persisto experiências, skills, projetos selecionados e redes sociais |
| **Redis** | Faço cache das respostas do GitHub e sessões auxiliares |

## Arquitetura

- **Routers** — organizei rotas por domínio (`landpage`, `admin`, `auth`)
- **Facades** — monto as respostas públicas a partir do banco e das integrações
- **ORM** — camada de acesso ao PostgreSQL com SQLAlchemy
- **Generators** — gero o currículo em PDF com ReportLab

Novos módulos em `routers/` são registrados automaticamente, sem precisar alterar o `main.py`.

## Stack

FastAPI · Pydantic · SQLAlchemy · Alembic · PostgreSQL · Redis · ReportLab · Docker

## Relação com o frontend

Esta API é consumida pelo meu [portfólio frontend](https://www.hudsondev.tech/). O site renderiza as seções; eu defino aqui o que existe, o que fica visível e quem pode alterar.

---

**Hudson Farias** — Software Developer · Fullstack Engineer · DevOps
