from database.roles import RolesORM


async def roles_map() -> dict[int, str]:
    async with RolesORM() as orm:
        roles = await orm.find_many()

    return {role.id: role.title for role in roles}


def role_title(role_id: int | None, titles: dict[int, str]) -> str | None:
    if role_id is None:
        return None

    return titles.get(role_id)
