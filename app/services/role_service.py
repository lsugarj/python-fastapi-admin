from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.mappers.role_mapper import RoleMapper
from app.repositorys.role_repo import RoleRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.role import RolePageQueryParams, RoleList, RoleRead, RoleCreate, RoleUpdate


class RoleService:

    @staticmethod
    async def create_role(data: RoleCreate, session: AsyncSession) -> IDResult:
        existing = await RoleRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.ROLE_ALREADY_EXISTS, "角色Code已经存在")
        role = RoleMapper.to_create_entity(data)
        role_id = await RoleRepository.create_role(role, data.permission_ids, session)
        return IDResult(id=role_id)


    @staticmethod
    async def update_role(role_id: int, data: RoleUpdate, session: AsyncSession) -> BoolResult:
        # DTO → update dict
        update_data = RoleMapper.to_update_dict(data)
        if not update_data:
            return BoolResult(success=False)
        # 执行更新
        is_success = await RoleRepository.update_role(role_id, update_data, data.permission_ids, session)
        if not is_success:
            raise BusinessException(Code.ROLE_NOT_FOUND, "角色不存在")
        return BoolResult(success=True)


    @staticmethod
    async def delete_role(role_id: int, session: AsyncSession) -> BoolResult:
        # 执行删除
        is_success = await RoleRepository.delete_role(role_id, session)
        if not is_success:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        return BoolResult(success=True)


    @staticmethod
    async def get_role_by_id(role_id: int, session: AsyncSession) -> RoleRead:
        role = await RoleRepository.get_role_by_id(role_id, session)
        if not role:
            raise BusinessException(Code.ROLE_NOT_FOUND, "角色不存在")
        data = RoleMapper.to_read_entity(role)
        return data


    @staticmethod
    async def get_role_list(session: AsyncSession) -> List[RoleList]:
        roles = await RoleRepository.get_role_list(session)
        items = [
            RoleMapper.to_list_entity(u) for u in roles
        ]
        return items


    @staticmethod
    async def get_role_page(params: RolePageQueryParams, session: AsyncSession) -> PageResult[RoleRead]:
        total, roles = await RoleRepository.get_role_page(params, session)
        items = [
            RoleMapper.to_read_entity(u) for u in roles
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )