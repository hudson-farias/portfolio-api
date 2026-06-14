from typing import Optional

from services.resume_sections import parse_csv_ids, parse_csv_slugs


def skill_matches_filter(skill, sections: set[str], skill_ids: set[int]) -> bool:
    if skill.id in skill_ids: return True
    if not sections: return True
    if 'skills' in sections: return True
    return False


def experience_matches_filter(experience_id: int, experience_ids: set[int]) -> bool:
    if not experience_ids: return True
    return experience_id in experience_ids


def tool_matches_filter(tool_id: int, tool_ids: set[int]) -> bool:
    if not tool_ids: return True
    return tool_id in tool_ids


def framework_matches_filter(framework_id: int, linked_language_ids: set[int], framework_ids: set[int], language_ids: set[int]) -> bool:
    if framework_id in framework_ids: return True
    if language_ids and linked_language_ids.intersection(language_ids): return True
    if not framework_ids and not language_ids: return True
    return False


def database_matches_filter(database_id: int, database_ids: set[int], sections: set[str]) -> bool:
    if database_id in database_ids: return True
    if not database_ids:
        if not sections: return True
        if 'databases' in sections: return True
    return False


def parse_resume_query(sections: Optional[str] = None, skill_ids: Optional[str] = None, tool_ids: Optional[str] = None, experience_ids: Optional[str] = None, framework_ids: Optional[str] = None, language_ids: Optional[str] = None, database_ids: Optional[str] = None, include_tools: bool = False):
    return {
        'sections': parse_csv_slugs(sections),
        'skill_ids': parse_csv_ids(skill_ids),
        'tool_ids': parse_csv_ids(tool_ids),
        'experience_ids': parse_csv_ids(experience_ids),
        'framework_ids': parse_csv_ids(framework_ids),
        'language_ids': parse_csv_ids(language_ids),
        'database_ids': parse_csv_ids(database_ids),
        'include_tools': include_tools or bool(parse_csv_ids(tool_ids)),
    }
