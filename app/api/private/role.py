from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session, get_read_session
from app.api.deps import require_role
from app.schemas.response import ResponseModel, Response
from app.schemas.common import IDResult, PageResult, BoolResult
from app.schemas.role import RoleCreate, RoleUpdate, RoleRead, RoleList, RolePage, RolePageQueryParams
from app.services.role_service import RoleService

router = APIRouter(prefix="/private/roles", dependencies=[Depends(require_role("admin"))])


@router.post("", response_model=ResponseModel[IDResult])
async def create_role(
    params: RoleCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await RoleService.create_role(params, session)
    return Response.success(data=result)


@router.patch("/detail/{role_id}", response_model=ResponseModel[BoolResult])
async def update_role(
    role_id: int,
    params: RoleUpdate,
    session: AsyncSession = Depends(get_session),
):
    data = await RoleService.update_role(role_id, params, session)
    return Response.success(data=data)


@router.delete("/detail/{role_id}", response_model=ResponseModel[BoolResult])
async def delete_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
):
    data = await RoleService.delete_role(role_id, session)
    return Response.success(data=data)


@router.get("/detail/{role_id}", response_model=ResponseModel[RoleRead])
async def get_role_by_id(
    role_id: int,
    session: AsyncSession = Depends(get_read_session),
):
    data = await RoleService.get_role_by_id(role_id, session)
    return Response.success(data=data)


@router.get("/list", response_model=ResponseModel[List[RoleList]])
async def get_role_list(
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await RoleService.get_role_list(session)
    return Response.success(data=page_result)


@router.get("/pages", response_model=ResponseModel[PageResult[RolePage]])
async def get_role_page(
    params: RolePageQueryParams = Depends(),
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await RoleService.get_role_page(params, session)
    return Response.success(data=page_result)