from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.models.rbac import Role
from app.repositorys.role_repo import RoleRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.role import RolePageQueryParams, RolePage, RoleList, RoleRead, RoleCreate, RoleUpdate


class RoleService:

    @staticmethod
    async def create_role(data: RoleCreate, session: AsyncSession) -> IDResult:
        existing = await RoleRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.ROLE_ALREADY_EXISTS, "Code已经存在")
        role = Role(code=data.code, name=data.name)
        role_id = await RoleRepository.create_role(role, data.menu_ids, session)
        return IDResult(id=role_id)


    @staticmethod
    async def update_role(role_id: int, data: RoleUpdate, session: AsyncSession) -> BoolResult:
        # 提取更新字段
        update_data = data.model_dump(exclude_unset=True, exclude={"menu_ids"})
        if not update_data:
            return BoolResult(success=False)
        # 直接 UPDATE
        is_success = await RoleRepository.update_role(role_id, update_data, data.menu_ids, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await RoleRepository.exists(role_id, session)
        if not exists:
            raise BusinessException(Code.ROLE_NOT_FOUND, "角色不存在")
        # 存在但没更新成功
        return BoolResult(success=False)


    @staticmethod
    async def delete_role(role_id: int, session: AsyncSession) -> BoolResult:
        # 直接 UPDATE
        is_success = await RoleRepository.delete_role(role_id, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await RoleRepository.exists(role_id, session)
        if not exists:
            raise BusinessException(Code.ROLE_NOT_FOUND, "角色不存在")
        # 存在但没删除成功
        return BoolResult(success=False)


    @staticmethod
    async def get_role_by_id(role_id: int, session: AsyncSession) -> RoleRead | None:
        role = await RoleRepository.get_role_by_id(role_id, session)
        if not role:
            raise BusinessException(Code.ROLE_NOT_FOUND, "角色不存在")
        return RoleRead.model_validate(role) if role else None


    @staticmethod
    async def get_role_list(session: AsyncSession) -> List[RoleList]:
        roles = await RoleRepository.get_role_list(session)
        items = [
            RoleList.model_validate(r) for r in roles
        ]
        return items


    @staticmethod
    async def get_role_page(params: RolePageQueryParams, session: AsyncSession) -> PageResult[RolePage]:
        total, roles = await RoleRepository.get_role_page(params, session)
        items = [
            RolePage.model_validate(r) for r in roles
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )