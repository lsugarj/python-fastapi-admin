from datetime import datetime, UTC
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete, insert
from sqlalchemy.orm import selectinload
from app.models.rbac import Role, RolePermission
from app.schemas.role import RolePageQueryParams


class RoleRepository:

    @staticmethod
    async def create_role(role: Role, permission_ids: list[int], session: AsyncSession) -> int:
        # 创建用户
        session.add(role)
        await session.flush()  # 拿到 role.id（不 commit）
        # 批量插入 role_permission
        if permission_ids:
            await session.execute(
                insert(RolePermission),
                [
                    {"role_id": role.id, "permission_id": permission_id}
                    for permission_id in permission_ids
                ]
            )
        return role.id

    @staticmethod
    async def update_role(role_id: int, update_data: dict, permission_ids: list[int], session: AsyncSession) -> bool:
        """
        返回：
        True  → 更新成功
        False → 没有匹配行（可能不存在 or 值相同）
        """
        # 更新角色
        result = await session.execute(
            update(Role)
            .where(Role.id == role_id)
            .values(**update_data)
        )

        # 如果角色不存在，直接返回
        if result.rowcount <= 0:
            return False
        # 删除角色旧权限数据
        await session.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        # 插入新菜单
        if permission_ids:
            await session.execute(
                insert(RolePermission),
                [
                    {"role_id": role_id, "permission_id": permission_id}
                    for permission_id in permission_ids
                ]
            )
        return True


    @staticmethod
    async def delete_role(role_id: int, session: AsyncSession) -> bool:
        """
       返回：
       True  → 更新成功
       False → 没有匹配行（可能不存在 or 值相同）
       """
        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(deleted_at=datetime.now(UTC))
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


    @staticmethod
    async def exists(role_id: int, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Role.id)
            .where( Role.id == role_id).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def exists_by_code(code: str, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(Role.id)
            .where( Role.code == code).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None


    @staticmethod
    async def get_role_by_id(role_id: int, session: AsyncSession) -> Role | None:
        stmt = (select(Role)
                .options(selectinload(Role.permissions))
                .where(Role.id == role_id))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


    @staticmethod
    async def get_role_list(session: AsyncSession) -> List[Role]:
        stmt = select(Role)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_role_page(params: RolePageQueryParams, session: AsyncSession):
        stmt = select(Role)

        # 动态条件
        if params.code:
            stmt = stmt.where(Role.code.contains(params.code))
        if params.name is not None:
            stmt = stmt.where(Role.name == params.name)

        # ===== 总数 =====
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        # ===== 分页 =====
        query_stmt = stmt.options(selectinload(Role.permissions)).offset(params.offset).limit(params.size)
        result = await session.execute(query_stmt)
        roles = result.scalars().all()

        return total, roles