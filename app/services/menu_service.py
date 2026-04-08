from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.models.rbac import Menu
from app.repositorys.menu_repo import MenuRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.menu import MenuList, MenuPageQueryParams, MenuPage, MenuCreate, \
    MenuUpdate, MenuRead


class MenuService:

    @staticmethod
    async def create_menu(data: MenuCreate, session: AsyncSession) -> IDResult:
        existing = await MenuRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.MENU_ALREADY_EXISTS, "Code已经存在")
        menu = Menu(
            **data.model_dump(
                include={
                    "code",
                    "name",
                    "type",
                    "icon",
                    "path",
                    "sort",
                    "is_visible",
                    "permission_id",
                }
            )
        )
        menu_id = await MenuRepository.create_menu(menu, session)
        return IDResult(id=menu_id)


    @staticmethod
    async def update_menu(menu_id: int, data: MenuUpdate, session: AsyncSession) -> BoolResult:
        # 提取更新字段
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return BoolResult(success=False)
        # 直接 UPDATE
        is_success = await MenuRepository.update_menu(menu_id, update_data, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await MenuRepository.exists(menu_id, session)
        if not exists:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        # 存在但没更新成功
        return BoolResult(success=False)


    @staticmethod
    async def delete_menu(menu_id: int, session: AsyncSession) -> BoolResult:
        # 直接删除
        is_success = await MenuRepository.delete_menu(menu_id, session)
        # 如果删除成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await MenuRepository.exists(menu_id, session)
        if not exists:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        # 存在但没删除成功
        return BoolResult(success=False)


    @staticmethod
    async def get_menu_by_id(menu_id: int, session: AsyncSession) -> MenuRead | None:
        menu = await MenuRepository.get_menu_by_id(menu_id, session)
        if not menu:
            raise BusinessException(Code.MENU_NOT_FOUND, "数据不存在")
        return MenuRead.model_validate(menu) if menu else None


    @staticmethod
    async def get_menu_list(session: AsyncSession) -> List[MenuList]:
        menus = await MenuRepository.get_menu_list(session)
        items = [
            MenuList.model_validate(m) for m in menus
        ]
        return items


    @staticmethod
    async def get_menu_page(params: MenuPageQueryParams, session: AsyncSession) -> PageResult[MenuPage]:
        total, menus = await MenuRepository.get_menu_page(params, session)
        items = [
            MenuPage.model_validate(m) for m in menus
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )