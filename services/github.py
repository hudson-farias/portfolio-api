from httpx import get

from utils.redis import set_cache, get_cache

from env import GITHUB_ACCESS_TOKEN


GITHUB_API_URL = 'https://api.github.com/users/hudson-farias/repos?per_page=100'
GITHUB_API_URL_PRIVATE = 'https://api.github.com/user/repos?per_page=100'


def github(is_auth: bool):
    return []
    data = get_cache(f'github-{is_auth}')
    if data: return data

    github_url = GITHUB_API_URL_PRIVATE if is_auth else GITHUB_API_URL

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if is_auth: headers['Authorization'] = f'Bearer {GITHUB_ACCESS_TOKEN}'

    response = get(github_url, headers = headers)
    projects = response.json()

    set_cache(f'github-{is_auth}', projects)
    return projects
