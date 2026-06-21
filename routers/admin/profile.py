from fastapi import Depends
from routers.admin import router, has_authenticated

from database.profile import ProfileORM
from database.profile_translations import ProfileTranslationsORM

from models.admin.profile import *


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


def translations_model(grouped, fields_model):
    def fields(data):
        if not data:
            return None
        return fields_model(**{key: data.get(key) for key in fields_model.model_fields.keys()})

    return ProfileTranslations(pt = fields(grouped.get('pt')), en = fields(grouped.get('en')))


def translations_payload(translations: ProfileTranslations):
    return {
        'pt': translations.pt.dict() if translations.pt else None,
        'en': translations.en.dict() if translations.en else None,
    }


async def response_data():
    async with ProfileORM() as orm:
        profile = await orm.find_one()

    grouped = {row.locale: row.dict() for row in profile.translations}

    return Profile(
        name = profile.name,
        last_name = profile.last_name,
        available = profile.available,
        email = profile.email,
        whatsapp = profile.whatsapp,
        linkedin = profile.linkedin,
        github = profile.github,
        gitlab = profile.gitlab,
        translations = translations_model(grouped, ProfileTranslationFields),
    )


@router.get('/profile', status_code = 200, response_model = Profile)
async def get():
    return await response_data()


@router.put('/profile', status_code = 201, response_model = Profile)
async def put(params: ProfileWrite, _: bool = Depends(has_authenticated)):
    async with ProfileORM() as orm:
        profile = await orm.find_one()
        await orm.update(
            id = profile.id,
            name = params.name,
            last_name = params.last_name,
            available = params.available,
            email = params.email,
            whatsapp = params.whatsapp,
            linkedin = params.linkedin,
            github = params.github,
            gitlab = params.gitlab,
        )

        await save_translations(profile.id, ProfileTranslationsORM, 'profile_id', translations_payload(params.translations))

    return await response_data()
