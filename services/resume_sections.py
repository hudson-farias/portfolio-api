STACK_SECTION_CATEGORIES = {
    'languages': [],
    'frameworks': [],
    'databases': [],
    'skills': [],
}


def parse_csv_ids(value: str | None) -> set[int]:
    if not value: return set()

    ids = set()

    for item in value.split(','):
        item = item.strip()
        if not item: continue
        ids.add(int(item))

    return ids


def parse_csv_slugs(value: str | None) -> set[str]:
    if not value: return set()

    slugs = set()

    for item in value.split(','):
        item = item.strip()
        if item in STACK_SECTION_CATEGORIES: slugs.add(item)

    return slugs
