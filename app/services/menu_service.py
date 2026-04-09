from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.mappers.menu_mapper import MenuMapper
from app.repositorys.menu_repo import MenuRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.menu import MenuList, MenuPageQueryParams, MenuCreate, \
    MenuUpdate, MenuRead


class MenuService:

    @staticmethod
    async def create_menu(data: MenuCreate, session: AsyncSession) -> IDResult:
        # 判断code是否已经存在
        existing = await MenuRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.MENU_ALREADY_EXISTS, "菜单Code已经存在")
        # DTO → Entity
        data = MenuMapper.to_create_entity(data)
        # 数据入库
        menu_id = await MenuRepository.create_menu(data, session)
        return IDResult(id=menu_id)


    @staticmethod
    async def update_menu(menu_id: int, data: MenuUpdate, session: AsyncSession) -> BoolResult:
        # DTO → update dict
        update_data = MenuMapper.to_update_dict(data)
        # 执行更新
        is_success = await MenuRepository.update_menu(menu_id, update_data, session)
        if not is_success:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        return BoolResult(success=True)


    @staticmethod
    async def delete_menu(menu_id: int, session: AsyncSession) -> BoolResult:
        # 执行删除
        is_success = await MenuRepository.delete_menu(menu_id, session)
        if not is_success:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        return BoolResult(success=True)


    @staticmethod
    async def get_menu_by_id(menu_id: int, session: AsyncSession) -> MenuRead:
        menu = await MenuRepository.get_menu_by_id(menu_id, session)
        if not menu:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        data = MenuMapper.to_read_entity(menu)
        return data


    @staticmethod
    async def get_menu_list(session: AsyncSession) -> List[MenuList]:
        menus = await MenuRepository.get_menu_list(session)
        items = [
            MenuMapper.to_list_entity(u) for u in menus
        ]
        return items


    @staticmethod
    async def get_menu_page(params: MenuPageQueryParams, session: AsyncSession) -> PageResult[MenuRead]:
        total, menus = await MenuRepository.get_menu_page(params, session)
        items = [
            MenuMapper.to_read_entity(u) for u in menus
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )