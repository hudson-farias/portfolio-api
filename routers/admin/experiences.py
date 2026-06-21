from fastapi import Depends, HTTPException, Query
from routers.admin import router, partial_authenticated, has_authenticated

from database.experiences import ExperiencesORM
from database.experience_translations import ExperienceTranslationsORM
from database.roles import RolesORM

from models.admin.experiences import *

from utils.sanitize import sanitize_html

from typing import Optional


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


def experience_to_model(experience):
    translations = experience_translations_model(experience)
    picked = [t for t in experience.translations if t.locale == 'pt']
    translation = picked[0] if picked else None

    role_translation = None
    if experience.role:
        role_picked = [t for t in experience.role.translations if t.locale == 'pt']
        role_translation = role_picked[0] if role_picked else None

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
        translations = translations,
    )


async def item_data(experience_id: int, is_auth: bool):
    async with ExperiencesORM() as orm:
        experience = await orm.find_one(id = experience_id)

    if not experience or (not is_auth and experience.hidden):
        raise HTTPException(status_code = 404, detail = 'Experiência não encontrada.')

    return experience_to_model(experience)


async def response_data(is_auth: bool, q: Optional[str] = None, role_id: Optional[int] = None, contract_type: Optional[ContractType] = None, hidden: Optional[bool] = None):
    experiences = await load_experiences(is_auth, q, role_id, contract_type, hidden)

    async with RolesORM() as orm:
        roles = await orm.find_many()

    role_items = []
    for role in roles:
        picked = [t for t in role.translations if t.locale == 'pt']
        translation = picked[0] if picked else None
        role_items.append(ExperienceRole(id = role.id, title = translation.title or '' if translation else '', active = role.active))

    return ExperiencesResponse(
        experiences = [experience_to_model(experience) for experience in experiences],
        roles = role_items,
    )


async def persist_experience(params: ExperienceBaseDTO, experience_id: Optional[int] = None):
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
