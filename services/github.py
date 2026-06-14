from httpx import get

from env import GITHUB_ACCESS_TOKEN


GITHUB_API_URL = 'https://api.github.com/users/hudson-farias/repos?per_page=100'
GITHUB_API_URL_PRIVATE = 'https://api.github.com/user/repos?per_page=100&type=owner&sort=updated'


def github(is_auth: bool):
    github_url = GITHUB_API_URL_PRIVATE if is_auth else GITHUB_API_URL

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if is_auth: headers['Authorization'] = f'Bearer {GITHUB_ACCESS_TOKEN}'

    response = get(github_url, headers = headers)
    if response.status_code != 200: return []

    projects = response.json()
    if not isinstance(projects, list): return []

    return projects
