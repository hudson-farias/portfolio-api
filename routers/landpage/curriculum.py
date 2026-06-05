from fastapi.responses import StreamingResponse

from routers.landpage import router

from generators.curriculum import Curriculum

@router.get('/curriculum')
async def get_curriculum():
    curriculum = Curriculum()
    pdf_buffer = await curriculum.generate()

    return StreamingResponse(pdf_buffer, media_type = 'application/pdf', headers = {'Content-Disposition': 'inline; filename="curriculum.pdf"'})
