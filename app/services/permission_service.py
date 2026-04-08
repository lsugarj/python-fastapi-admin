from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.models.rbac import Permission
from app.repositorys.permission_repo import PermissionRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.permission import PermissionList, PermissionPageQueryParams, PermissionPage, PermissionCreate, \
    PermissionUpdate, PermissionRead


class PermissionService:

    @staticmethod
    async def create_permission(data: PermissionCreate, session: AsyncSession) -> IDResult:
        existing = await PermissionRepository.exists_by_code(data.code, session)
        if existing:
            raise BusinessException(Code.PERMISSION_ALREADY_EXISTS, "Code已经存在")
        permission = Permission(code=data.code, name=data.name, path=data.path, method=data.method)
        permission_id = await PermissionRepository.create_permission(permission, session)
        return IDResult(id=permission_id)


    @staticmethod
    async def update_permission(permission_id: int, data: PermissionUpdate, session: AsyncSession) -> BoolResult:
        # 提取更新字段
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return BoolResult(success=False)
        # 直接 UPDATE
        is_success = await PermissionRepository.update_permission(permission_id, update_data, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await PermissionRepository.exists(permission_id, session)
        if not exists:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        # 存在但没更新成功
        return BoolResult(success=False)


    @staticmethod
    async def delete_permission(permission_id: int, session: AsyncSession) -> BoolResult:
        # 直接删除
        is_success = await PermissionRepository.delete_permission(permission_id, session)
        # 如果删除成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await PermissionRepository.exists(permission_id, session)
        if not exists:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        # 存在但没删除成功
        return BoolResult(success=False)


    @staticmethod
    async def get_permission_by_id(permission_id: int, session: AsyncSession) -> PermissionRead | None:
        permission = await PermissionRepository.get_permission_by_id(permission_id, session)
        if not permission:
            raise BusinessException(Code.PERMISSION_NOT_FOUND, "数据不存在")
        return PermissionRead.model_validate(permission) if permission else None


    @staticmethod
    async def get_permission_list(session: AsyncSession) -> List[PermissionList]:
        permissions = await PermissionRepository.get_permission_list(session)
        items = [
            PermissionList.model_validate(u) for u in permissions
        ]
        return items


    @staticmethod
    async def get_permission_page(params: PermissionPageQueryParams, session: AsyncSession) -> PageResult[PermissionPage]:
        total, permissions = await PermissionRepository.get_permission_page(params, session)
        items = [
            PermissionPage.model_validate(u) for u in permissions
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )