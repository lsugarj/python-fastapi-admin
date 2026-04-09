from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.mappers.permission_mapper import PermissionMapper
from app.repositorys.permission_repo import PermissionRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.permission import PermissionList, PermissionPageQueryParams, PermissionCreate, \
    PermissionUpdate, PermissionRead


class PermissionService:

    @staticmethod
    async def create_permission(data: PermissionCreate, session: AsyncSession) -> IDResult:
        # 判断code是否已经存在
        existing = await PermissionRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.PERMISSION_ALREADY_EXISTS, "权限Code已经存在")
        # DTO → Entity
        data = PermissionMapper.to_create_entity(data)
        # 数据入库
        permission_id = await PermissionRepository.create_permission(data, session)
        return IDResult(id=permission_id)


    @staticmethod
    async def update_permission(permission_id: int, data: PermissionUpdate, session: AsyncSession) -> BoolResult:
        # DTO → update dict
        update_data = PermissionMapper.to_update_dict(data)
        # 执行更新
        is_success = await PermissionRepository.update_permission(permission_id, update_data, session)
        if not is_success:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        return BoolResult(success=True)


    @staticmethod
    async def delete_permission(permission_id: int, session: AsyncSession) -> BoolResult:
        # 执行删除
        is_success = await PermissionRepository.delete_permission(permission_id, session)
        if not is_success:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        return BoolResult(success=True)


    @staticmethod
    async def get_permission_by_id(permission_id: int, session: AsyncSession) -> PermissionRead:
        permission = await PermissionRepository.get_permission_by_id(permission_id, session)
        if not permission:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        # DTO → entity
        data = PermissionMapper.to_read_entity(permission)
        return data


    @staticmethod
    async def get_permission_list(session: AsyncSession) -> List[PermissionList]:
        permissions = await PermissionRepository.get_permission_list(session)
        items = [
            PermissionMapper.to_list_entity(u) for u in permissions
        ]
        return items


    @staticmethod
    async def get_permission_page(params: PermissionPageQueryParams, session: AsyncSession) -> PageResult[PermissionRead]:
        total, permissions = await PermissionRepository.get_permission_page(params, session)
        items = [
            PermissionMapper.to_read_entity(u) for u in permissions
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )