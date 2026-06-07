from database.experiences import ExperiencesORM


async def experience_counts() -> dict[int, int]:
    async with ExperiencesORM() as orm:
        experiences = await orm.find_many()

    counts: dict[int, int] = {}

    for experience in experiences:
        if experience.role_id is None:
            continue

        counts[experience.role_id] = counts.get(experience.role_id, 0) + 1

    return counts
