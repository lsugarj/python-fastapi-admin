from datetime import datetime, UTC
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete, insert
from sqlalchemy.orm import selectinload
from app.models.rbac import User, UserRole
from app.schemas.user import UserPageQueryParams


class UserRepository:

    @staticmethod
    async def create_user(user: User, role_ids: list[int], session: AsyncSession) -> int:
        # 创建用户
        session.add(user)
        await session.flush()  # 拿到 user.id（不 commit）
        # 批量插入 user_role
        if role_ids:
            await session.execute(
                insert(UserRole),
                [
                    {"user_id": user.id, "role_id": role_id}
                    for role_id in role_ids
                ]
            )
        return user.id

    @staticmethod
    async def update_user(user_id: int, update_data: dict, role_ids: list[int], session: AsyncSession) -> bool:
        """
        返回：
        True  → 更新成功
        False → 没有匹配行（可能不存在 or 值相同）
        """
        # 更新用户
        result = await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )

        # 如果用户不存在，直接返回
        if result.rowcount <= 0:
            return False
        # 删除旧角色（中间表）
        await session.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        # 插入新角色
        if role_ids:
            await session.execute(
                insert(UserRole),
                [
                    {"user_id": user_id, "role_id": role_id}
                    for role_id in role_ids
                ]
            )
        return True


    @staticmethod
    async def update_user_token_version(user_id: int, token_version: int, session: AsyncSession) -> bool:
        """
       返回：
       True  → 更新成功
       False → 没有匹配行（可能不存在 or 值相同）
       """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(token_version=token_version)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> bool:
        """
       返回：
       True  → 更新成功
       False → 没有匹配行（可能不存在 or 值相同）
       """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(deleted_at=datetime.now(UTC))
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


    @staticmethod
    async def exists(user_id: int, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(User.id)
            .where( User.id == user_id).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def exists_by_username(username: str, session: AsyncSession) -> bool:
        """
        判断用户是否存在（未删除）
        """
        stmt = (
            select(User.id)
            .where( User.username == username).limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_user_for_login(username: str, session: AsyncSession) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    @staticmethod
    async def get_current_user(user_id: int, session: AsyncSession) -> User | None:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
        stmt = (select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_list(session: AsyncSession) -> List[User]:
        stmt = select(User).where(User.is_active == True)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_user_page(params: UserPageQueryParams, session: AsyncSession):
        stmt = select(User)

        # 动态条件
        if params.username:
            stmt = stmt.where(User.username.contains(params.username))
        if params.is_active is not None:
            stmt = stmt.where(User.is_active == params.is_active)

        # ===== 总数 =====
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await session.execute(count_stmt)).scalar_one()

        # ===== 分页 =====
        query_stmt = stmt.options(selectinload(User.roles)).offset(params.offset).limit(params.size)
        result = await session.execute(query_stmt)
        users = result.scalars().all()

        return total, users