from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete
from sqlalchemy.orm import selectinload

from app.models.rbac import Menu
from app.schemas.menu import MenuPageQueryParams


class MenuRepository:

    @staticmethod
    async def create_menu(menu: Menu, session: AsyncSession) -> int:
        session.add(menu)
        await session.flush()
        return menu.id

    @staticmethod
    async def update_menu(menu_id: int, update_data: dict, session: AsyncSession) -> bool:
        """
        返回：
        True  → 更新成功
        False → 没有匹配行（可能不存在 or 值相同）
        """
        stmt = (
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**update_data)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def delete_menu(menu_id: int, session: AsyncSession) -> bool:
        """
       返回：
       True  → 更新成功
       False → 没有匹配行（可能不存在 or 值相同）
       """
        stmt = (
            delete(Menu)
            .where(Menu.id == menu_id)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


    @staticmethod
    async def exists(menu_id: int, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Menu.id)
            .where(Menu.id == menu_id).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def exists_by_code(code: str, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Menu.id)
            .where(Menu.code == code).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


    @staticmethod
    async def get_menu_by_id(menu_id: int, session: AsyncSession) -> Menu | None:
        stmt = (select(Menu)
                .options(selectinload(Menu.permission))
                .where(Menu.id == menu_id))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_menu_list(session: AsyncSession) -> List[Menu]:
        stmt = select(Menu)
        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_menu_page(params: MenuPageQueryParams, session: AsyncSession):
        stmt = select(Menu)

        # 动态条件
        if params.name:
            stmt = stmt.where(Menu.name.contains(params.name))
        if params.path:
            stmt = stmt.where(Menu.path.contains(params.path))

        # ===== 总数 =====
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        # ===== 分页 =====
        query_stmt = stmt.options(selectinload(Menu.permission)).offset(params.offset).limit(params.size)
        result = await session.execute(query_stmt)
        menus = result.scalars().all()

        return total, menus