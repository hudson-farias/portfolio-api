from bleach import clean


ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title', 'target', 'rel']}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(value: str):
    return clean(
        value,
        tags = ALLOWED_TAGS,
        attributes = ALLOWED_ATTRIBUTES,
        protocols = ALLOWED_PROTOCOLS,
        strip = True,
    )
