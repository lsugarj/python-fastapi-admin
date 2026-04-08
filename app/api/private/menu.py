from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session, get_read_session
from app.api.deps import require_role
from app.schemas.response import ResponseModel, Response
from app.schemas.common import IDResult, PageResult, BoolResult
from app.schemas.menu import MenuCreate, MenuPageQueryParams, MenuUpdate, MenuPage, \
    MenuList, MenuRead
from app.services.menu_service import MenuService


router = APIRouter(prefix="/private/menus", dependencies=[Depends(require_role("admin"))])


@router.post("", response_model=ResponseModel[IDResult])
async def create_menu(
    params: MenuCreate,
    session: AsyncSession = Depends(get_session),
):
    result = await MenuService.create_menu(params, session)
    return Response.success(data=result)


@router.patch("/detail/{menu_id}", response_model=ResponseModel[BoolResult])
async def update_menu(
    menu_id: int,
    params: MenuUpdate,
    session: AsyncSession = Depends(get_session),
):
    data = await MenuService.update_menu(menu_id, params, session)
    return Response.success(data=data)


@router.delete("/detail/{menu_id}", response_model=ResponseModel[BoolResult])
async def delete_menu(
    menu_id: int,
    session: AsyncSession = Depends(get_session),
):
    data = await MenuService.delete_menu(menu_id, session)
    return Response.success(data=data)


@router.get("/detail/{menu_id}", response_model=ResponseModel[MenuRead])
async def get_menu_by_id(
    menu_id: int,
    session: AsyncSession = Depends(get_read_session),
):
    data = await MenuService.get_menu_by_id(menu_id, session)
    return Response.success(data=data)


@router.get("/list", response_model=ResponseModel[List[MenuList]])
async def get_menu_list(
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await MenuService.get_menu_list(session)
    return Response.success(data=page_result)


@router.get("/pages", response_model=ResponseModel[PageResult[MenuPage]])
async def get_menu_page(
    params: MenuPageQueryParams = Depends(),
    session: AsyncSession = Depends(get_read_session),
):
    page_result = await MenuService.get_menu_page(params, session)
    return Response.success(data=page_result)