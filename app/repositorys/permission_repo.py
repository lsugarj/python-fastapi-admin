from datetime import UTC, datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.rbac import Permission
from app.schemas.permission import PermissionPageQueryParams


class PermissionRepository:

    @staticmethod
    async def create_permission(permission: Permission, session: AsyncSession) -> int:
        session.add(permission)
        await session.flush()
        return permission.id

    @staticmethod
    async def update_permission(permission_id: int, update_data: dict, session: AsyncSession) -> bool:
        """
        返回：
        int → 影响行数（rowcount）
        """
        stmt = (
            update(Permission)
            .where(Permission.id == permission_id)
            .values(**update_data)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def delete_permission(permission_id: int, session: AsyncSession) -> bool:
        """
       返回：
       True  → 更新成功
       False → 没有匹配行（可能不存在 or 值相同）
       """
        stmt = (
            update(Permission)
            .where(Permission.id == permission_id)
            .values(deleted_at=datetime.now(UTC))
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


    @staticmethod
    async def exists(permission_id: int, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Permission.id)
            .where(Permission.id == permission_id).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def exists_by_code(code: str, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Permission.id)
            .where(Permission.code == code).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


    @staticmethod
    async def get_permission_by_id(id: int, session: AsyncSession) -> Permission | None:
        stmt = select(Permission).where(Permission.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_permission_list(session: AsyncSession) -> List[Permission]:
        stmt = select(Permission)
        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_permission_page(params: PermissionPageQueryParams, session: AsyncSession):
        stmt = select(Permission)

        # 动态条件
        if params.code:
            stmt = stmt.where(Permission.code.contains(params.code))
        if params.name:
            stmt = stmt.where(Permission.name.contains(params.name))
        if params.path:
            stmt = stmt.where(Permission.path.contains(params.path))

        # ===== 总数 =====
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        # ===== 分页 =====
        query_stmt = stmt.offset(params.offset).limit(params.size)
        result = await session.execute(query_stmt)
        permissions = result.scalars().all()

        return total, permissions