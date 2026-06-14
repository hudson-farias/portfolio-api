from typing import Optional

from fastapi.responses import StreamingResponse
from fastapi import Query

from routers.landpage import router

from generators.curriculum import Curriculum
from services.resume_filters import parse_resume_query


async def resume_pdf(filters: dict):
    curriculum = Curriculum(filters)
    pdf_buffer = await curriculum.generate()

    return StreamingResponse(
        pdf_buffer,
        media_type = 'application/pdf',
        headers = {'Content-Disposition': 'inline; filename="resume.pdf"'},
    )


@router.get('/resume', status_code = 200)
async def get_resume(sections: Optional[str] = Query(None), skill_ids: Optional[str] = Query(None), tool_ids: Optional[str] = Query(None), experience_ids: Optional[str] = Query(None), framework_ids: Optional[str] = Query(None), language_ids: Optional[str] = Query(None), database_ids: Optional[str] = Query(None), include_tools: bool = Query(False)):
    filters = parse_resume_query(sections, skill_ids, tool_ids, experience_ids, framework_ids, language_ids, database_ids, include_tools)
    return await resume_pdf(filters)
