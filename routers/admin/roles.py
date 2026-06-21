from fastapi import Depends, HTTPException, Query
from routers.admin import router, partial_authenticated, has_authenticated

from database.roles import RolesORM
from database.role_translations import RoleTranslationsORM

from models.admin.roles import *

from services.roles import experience_counts

from typing import List, Optional


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


def _role_filters(is_auth: bool, seniority: Optional[Seniority] = None, show: Optional[bool] = None, active: Optional[bool] = None, featured: Optional[bool] = None):
    filters = {key: value for key, value in {
        'seniority': seniority,
        'show': show,
        'featured': featured,
    }.items() if value is not None}

    if not is_auth:
        filters['active'] = True
    elif active is not None:
        filters['active'] = active

    return filters


async def load_roles(is_auth: bool, q: Optional[str] = None, seniority: Optional[Seniority] = None, show: Optional[bool] = None, active: Optional[bool] = None, featured: Optional[bool] = None):
    async with RolesORM() as orm:
        roles = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['category'],
            **_role_filters(is_auth, seniority, show, active, featured),
        )

    roles.sort(key = lambda role: (role.sort_order, role.id))
    return roles


def role_translations_model(role):
    grouped = {row.locale: row.dict() for row in role.translations}

    def fields(data):
        if not data:
            return None
        return RoleTranslationFields(**{key: data.get(key) for key in RoleTranslationFields.model_fields.keys()})

    return RoleTranslations(pt = fields(grouped.get('pt')), en = fields(grouped.get('en')))


def translations_payload(translations: RoleTranslations):
    return {
        'pt': translations.pt.dict() if translations.pt else None,
        'en': translations.en.dict() if translations.en else None,
    }


async def role_to_model(role, counts: dict):
    translations = role_translations_model(role)
    picked = [t for t in role.translations if t.locale == 'pt']
    translation = picked[0] if picked else None

    return Role(
        id = role.id,
        title = translation.title or '' if translation else '',
        category = role.category,
        seniority = role.seniority,
        show = role.show,
        featured = role.featured,
        active = role.active,
        sort_order = role.sort_order,
        color = role.color,
        icon = role.icon,
        translations = translations,
        experience_count = counts.get(role.id, 0),
    )


async def response_data(is_auth: bool, q: Optional[str] = None, seniority: Optional[Seniority] = None, show: Optional[bool] = None, active: Optional[bool] = None, featured: Optional[bool] = None):
    counts = await experience_counts()
    roles = await load_roles(is_auth, q, seniority, show, active, featured)
    return [await role_to_model(role, counts) for role in roles]


async def item_data(role_id: int, is_auth: bool):
    async with RolesORM() as orm:
        role = await orm.find_one(id = role_id)

    if not role or (not is_auth and not role.active):
        raise HTTPException(status_code = 404, detail = 'Cargo não encontrado.')

    counts = await experience_counts()
    return await role_to_model(role, counts)


async def persist_role(params: RoleDTO, role_id: Optional[int] = None):
    payload = {
        'category': params.category,
        'seniority': params.seniority,
        'show': params.show,
        'featured': params.featured,
        'active': params.active,
        'sort_order': params.sort_order,
        'color': params.color,
        'icon': params.icon,
    }

    async with RolesORM() as orm:
        if role_id is None:
            await orm.create(**payload)
            roles = await orm.find_many()
            role = max(roles, key = lambda item: item.id)
        else:
            await orm.update(id = role_id, **payload)
            role = await orm.find_one(id = role_id)

        await save_translations(role.id, RoleTranslationsORM, 'role_id', translations_payload(params.translations))


@router.get('/roles', status_code = 200, response_model = List[Role])
async def get(is_auth: bool = Depends(partial_authenticated), q: Optional[str] = Query(None), seniority: Optional[Seniority] = Query(None), show: Optional[bool] = Query(None), active: Optional[bool] = Query(None), featured: Optional[bool] = Query(None)):
    return await response_data(is_auth, q, seniority, show, active, featured)


@router.get('/roles/{role_id}', status_code = 200, response_model = Role)
async def get_one(role_id: int, is_auth: bool = Depends(partial_authenticated)):
    return await item_data(role_id, is_auth)


@router.post('/roles', status_code = 201, response_model = List[Role])
async def post(params: RoleDTO, is_auth: bool = Depends(has_authenticated)):
    await persist_role(params)
    return await response_data(is_auth)


@router.put('/roles/{role_id}', status_code = 201, response_model = List[Role])
async def put(role_id: int, params: RoleDTO, is_auth: bool = Depends(has_authenticated)):
    await persist_role(params, role_id)
    return await response_data(is_auth)


@router.delete('/roles/{role_id}', status_code = 201, response_model = List[Role])
async def delete(role_id: int, is_auth: bool = Depends(has_authenticated)):
    async with RolesORM() as orm: await orm.delete(id = role_id)
    return await response_data(is_auth)
