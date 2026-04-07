from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session, get_read_session
from app.api.deps import get_current_user
from app.schemas.response import ResponseModel, Response
from app.schemas.common import IDResult, PageResult, BoolResult
from app.schemas.permission import PermissionCreate, PermissionPageQueryParams, PermissionUpdate, PermissionPage, \
    PermissionList, PermissionRead
from app.services.permission_service import PermissionService


router = APIRouter(prefix="/private/permissions", dependencies=[Depends(get_current_user)])


@router.post("", response_model=ResponseModel[IDResult])
async def create_permission(
    params: PermissionCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await PermissionService.create_permission(params, session)
    return Response.success(data=result)


@router.patch("/detail/{permission_id}", response_model=ResponseModel[BoolResult])
async def update_permission(
    permission_id: int,
    params: PermissionUpdate,
    session: AsyncSession = Depends(get_session),
):
    data = await PermissionService.update_permission(permission_id, params, session)
    return Response.success(data=data)


@router.delete("/detail/{permission_id}", response_model=ResponseModel[BoolResult])
async def get_permission_by_id(
    permission_id: int,
    session: AsyncSession = Depends(get_session),
):
    data = await PermissionService.delete_permission(permission_id, session)
    return Response.success(data=data)


@router.get("/detail/{permission_id}", response_model=ResponseModel[PermissionRead])
async def get_permission_by_id(
    permission_id: int,
    session: AsyncSession = Depends(get_read_session),
):
    data = await PermissionService.get_permission_by_id(permission_id, session)
    return Response.success(data=data)


@router.get("/list", response_model=ResponseModel[List[PermissionList]])
async def get_permission_list(
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await PermissionService.get_permission_list(session)
    return Response.success(data=page_result)


@router.get("/pages", response_model=ResponseModel[PageResult[PermissionPage]])
async def get_permission_page(
    params: PermissionPageQueryParams = Depends(),
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await PermissionService.get_permission_page(params, session)
    return Response.success(data=page_result)