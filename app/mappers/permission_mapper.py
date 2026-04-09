from app.models.rbac import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionList, PermissionRead


class PermissionMapper:

    CREATE_FIELDS = {"code", "name", "path", "method"}
    UPDATE_FIELDS = {"name", "path", "method"}

    @staticmethod
    def to_create_entity(data: PermissionCreate) -> Permission:
        return Permission(**data.model_dump(include=PermissionMapper.CREATE_FIELDS))


    @staticmethod
    def to_update_dict(data: PermissionUpdate) -> dict:
        return data.model_dump(
            include=PermissionMapper.UPDATE_FIELDS,
            exclude_unset=True
        )

    @staticmethod
    def to_list_entity(data: Permission) -> PermissionList:
        return PermissionList.model_validate(data)

    @staticmethod
    def to_read_entity(data: Permission) -> PermissionRead:
        return PermissionRead.model_validate(data)