from fastapi import Depends, HTTPException, Query
from routers.admin import router, partial_authenticated, has_authenticated

from database.experiences import ExperiencesORM
from database.experience_translations import ExperienceTranslationsORM
from database.experience_frameworks import ExperienceFrameworksORM
from database.frameworks import FrameworksORM
from database.roles import RolesORM

from models.admin.experiences import *

from utils.sanitize import sanitize_html

from typing import Dict, List, Optional


async def save_translations(entity_id, translation_orm, foreign_key, by_locale):
    for locale, fields in by_locale.items():
        if locale not in ('pt', 'en') or not fields:
            continue

        filters = {foreign_key: entity_id, 'locale': locale}

        async with translation_orm() as orm:
            existing = await orm.find_one(**filters)

            if existing:
                await orm.update(id = existing.id, **fields)
            else:
                await orm.create(**filters, **fields)


async def load_experience_framework_ids():
    async with ExperienceFrameworksORM() as orm: relations = await orm.find_many()

    by_experience: Dict[int, List[int]] = {}

    for relation in relations:
        by_experience.setdefault(relation.experience_id, []).append(relation.framework_id)

    return by_experience


async def load_framework_refs(framework_ids: List[int]):
    if not framework_ids: return []

    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    frameworks_by_id = {framework.id: framework for framework in frameworks}

    refs = [
        FrameworkRef(**frameworks_by_id[framework_id].dict())
        for framework_id in framework_ids
        if framework_id in frameworks_by_id
    ]
    refs.sort(key = lambda item: (item.name.lower(), item.id))

    return refs


async def validate_framework_ids(framework_ids: List[int]):
    if not framework_ids: return

    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    existing_ids = {framework.id for framework in frameworks}
    invalid = set(framework_ids) - existing_ids

    if invalid: raise HTTPException(status_code = 400, detail = 'Um ou mais frameworks informados não existem.')


async def sync_relations(experience_id: int, framework_ids: List[int]):
    async with ExperienceFrameworksORM() as orm: await orm.delete(experience_id = experience_id)

    unique_ids = list(dict.fromkeys(framework_ids))
    for framework_id in unique_ids:
        async with ExperienceFrameworksORM() as orm:
            await orm.create(experience_id = experience_id, framework_id = framework_id)


def _experience_filters(is_auth: bool, role_id: Optional[int] = None, contract_type: Optional[ContractType] = None, hidden: Optional[bool] = None):
    filters = {key: value for key, value in {
        'role_id': role_id,
        'contract_type': contract_type,
    }.items() if value is not None}

    if not is_auth: filters['hidden'] = False
    elif hidden is not None: filters['hidden'] = hidden

    return filters


async def load_experiences(is_auth: bool, q: Optional[str] = None, role_id: Optional[int] = None, contract_type: Optional[ContractType] = None, hidden: Optional[bool] = None):
    async with ExperiencesORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['company'],
            **_experience_filters(is_auth, role_id, contract_type, hidden),
        )


def experience_translations_model(experience):
    grouped = {row.locale: row.dict() for row in experience.translations}

    def fields(data):
        if not data:
            return None
        return ExperienceTranslationFields(**{key: data.get(key) for key in ExperienceTranslationFields.model_fields.keys()})

    return ExperienceTranslations(pt = fields(grouped.get('pt')), en = fields(grouped.get('en')))


def translations_payload(translations: ExperienceTranslations):
    payload = {
        'pt': translations.pt.dict() if translations.pt else None,
        'en': translations.en.dict() if translations.en else None,
    }

    if payload['pt'] and payload['pt'].get('description'):
        payload['pt']['description'] = sanitize_html(payload['pt']['description'])

    return payload


def experience_to_model(experience, framework_ids_by_experience: Dict[int, List[int]], framework_refs_by_id: Dict[int, FrameworkRef]):
    translations = experience_translations_model(experience)
    picked = [t for t in experience.translations if t.locale == 'pt']
    translation = picked[0] if picked else None

    role_translation = None
    if experience.role:
        role_picked = [t for t in experience.role.translations if t.locale == 'pt']
        role_translation = role_picked[0] if role_picked else None

    framework_ids = framework_ids_by_experience.get(experience.id, [])
    frameworks = [
        framework_refs_by_id[framework_id]
        for framework_id in framework_ids
        if framework_id in framework_refs_by_id
    ]

    return Experience(
        id = experience.id,
        company = experience.company,
        period = translation.period or '' if translation else '',
        description = translation.description or '' if translation else '',
        role_id = experience.role_id,
        contract_type = experience.contract_type,
        live_url = experience.live_url,
        hidden = experience.hidden,
        role_title = role_translation.title if role_translation else None,
        framework_ids = framework_ids,
        frameworks = frameworks,
        translations = translations,
    )


async def framework_refs_by_id():
    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    frameworks.sort(key = lambda framework: (framework.sort_order, framework.id))

    return {framework.id: FrameworkRef(**framework.dict()) for framework in frameworks}


async def item_data(experience_id: int, is_auth: bool):
    async with ExperiencesORM() as orm:
        experience = await orm.find_one(id = experience_id)

    if not experience or (not is_auth and experience.hidden):
        raise HTTPException(status_code = 404, detail = 'Experiência não encontrada.')

    framework_ids_by_experience = await load_experience_framework_ids()
    refs_by_id = await framework_refs_by_id()

    return experience_to_model(experience, framework_ids_by_experience, refs_by_id)


async def response_data(is_auth: bool, q: Optional[str] = None, role_id: Optional[int] = None, contract_type: Optional[ContractType] = None, hidden: Optional[bool] = None):
    experiences = await load_experiences(is_auth, q, role_id, contract_type, hidden)
    framework_ids_by_experience = await load_experience_framework_ids()
    refs_by_id = await framework_refs_by_id()

    async with RolesORM() as orm:
        roles = await orm.find_many()

    role_items = []
    for role in roles:
        picked = [t for t in role.translations if t.locale == 'pt']
        translation = picked[0] if picked else None
        role_items.append(ExperienceRole(id = role.id, title = translation.title or '' if translation else '', active = role.active))

    return ExperiencesResponse(
        experiences = [experience_to_model(experience, framework_ids_by_experience, refs_by_id) for experience in experiences],
        roles = role_items,
    )


async def persist_experience(params: ExperienceBaseDTO, experience_id: Optional[int] = None):
    await validate_framework_ids(params.framework_ids)

    payload = {
        'company': params.company,
        'role_id': params.role_id,
        'contract_type': params.contract_type,
        'live_url': params.live_url,
        'hidden': params.hidden,
    }

    async with ExperiencesORM() as orm:
        if experience_id is None:
            await orm.create(**payload)
            experiences = await orm.find_many()
            experience = max(experiences, key = lambda item: item.id)
        else:
            await orm.update(id = experience_id, **payload)
            experience = await orm.find_one(id = experience_id)

        await save_translations(experience.id, ExperienceTranslationsORM, 'experience_id', translations_payload(params.translations))
        await sync_relations(experience.id, params.framework_ids)


@router.get('/experiences', status_code = 200, response_model = ExperiencesResponse)
async def get_experiences(is_auth: bool = Depends(partial_authenticated), q: Optional[str] = Query(None), role_id: Optional[int] = Query(None), contract_type: Optional[ContractType] = Query(None), hidden: Optional[bool] = Query(None)):
    return await response_data(is_auth, q, role_id, contract_type, hidden)


@router.get('/experiences/{experience_id}', status_code = 200, response_model = Experience)
async def get_experience(experience_id: int, is_auth: bool = Depends(partial_authenticated)):
    return await item_data(experience_id, is_auth)


@router.post('/experiences', status_code = 201, response_model = ExperiencesResponse)
async def post_experience(params: ExperienceBaseDTO, is_auth: bool = Depends(has_authenticated)):
    await persist_experience(params)
    return await response_data(is_auth)


@router.put('/experiences/{experience_id}', status_code = 201, response_model = ExperiencesResponse)
async def put_experience(experience_id: int, params: ExperienceBaseDTO, is_auth: bool = Depends(has_authenticated)):
    await persist_experience(params, experience_id)
    return await response_data(is_auth)


@router.delete('/experiences/{experience_id}', status_code = 201, response_model = ExperiencesResponse)
async def delete_experience(experience_id: int, is_auth: bool = Depends(has_authenticated)):
    async with ExperiencesORM() as orm: await orm.delete(id = experience_id)
    return await response_data(is_auth)
