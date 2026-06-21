from fastapi import Depends, HTTPException, Query
from routers.admin import router, has_authenticated

from database.tools import ToolsORM

from models.admin.tools import *

from typing import List, Optional


async def load_tools(q: Optional[str] = None):
    async with ToolsORM() as orm:
        tools = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon', 'url'],
        )

    tools.sort(key = lambda tool: (tool.sort_order, tool.id))
    return tools


async def response_data(q: Optional[str] = None):
    tools = await load_tools(q)
    return [Tool(**tool.dict()) for tool in tools]


async def next_sort_order():
    async with ToolsORM() as orm: tools = await orm.find_many()
    if not tools: return 0
    return max(tool.sort_order for tool in tools) + 1


async def item_data(tool_id: int):
    async with ToolsORM() as orm:
        tool = await orm.find_one(id = tool_id)

    if not tool:
        raise HTTPException(status_code = 404, detail = 'Ferramenta não encontrada.')

    return Tool(**tool.dict())


@router.get('/tools', status_code = 200, response_model = List[Tool])
async def get(q: Optional[str] = Query(None)):
    return await response_data(q)


@router.get('/tools/{tool_id}', status_code = 200, response_model = Tool)
async def get_one(tool_id: int):
    return await item_data(tool_id)


@router.put('/tools/reorder', status_code = 201, response_model = List[Tool])
async def reorder(params: ToolReorderDTO, _: bool = Depends(has_authenticated)):
    async with ToolsORM() as orm: tools = await orm.find_many()

    existing_ids = {tool.id for tool in tools}
    if set(params.ids) != existing_ids: raise HTTPException(status_code = 400, detail = 'Informe todos os IDs das ferramentas na nova ordem.')

    async with ToolsORM() as orm:
        for index, tool_id in enumerate(params.ids): await orm.update(id = tool_id, sort_order = index)

    return await response_data()


@router.post('/tools', status_code = 201, response_model = List[Tool])
async def post(params: ToolWriteDTO, _: bool = Depends(has_authenticated)):
    payload = params.dict()
    payload['sort_order'] = await next_sort_order()

    async with ToolsORM() as orm: await orm.create(**payload)
    return await response_data()


@router.put('/tools/{tool_id}', status_code = 201, response_model = List[Tool])
async def put(tool_id: int, params: ToolWriteDTO, _: bool = Depends(has_authenticated)):
    async with ToolsORM() as orm: current = await orm.find_one(id = tool_id)
    if not current: raise HTTPException(status_code = 404, detail = 'Ferramenta não encontrada.')

    payload = params.dict()
    payload['sort_order'] = current.sort_order

    async with ToolsORM() as orm: await orm.update(id = tool_id, **payload)
    return await response_data()


@router.delete('/tools/{tool_id}', status_code = 201, response_model = List[Tool])
async def delete(tool_id: int, _: bool = Depends(has_authenticated)):
    async with ToolsORM() as orm: await orm.delete(id = tool_id)
    return await response_data()
