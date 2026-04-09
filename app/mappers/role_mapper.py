from app.models.rbac import Role
from app.schemas.role import RoleCreate, RoleUpdate, RoleList, RoleRead


class RoleMapper:

    CREATE_FIELDS = {"code", "name", "is_active"}
    UPDATE_FIELDS = {"name", "is_active"}

    @staticmethod
    def to_create_entity(data: RoleCreate) -> Role:
        return Role(**data.model_dump(include=RoleMapper.CREATE_FIELDS))


    @staticmethod
    def to_update_dict(data: RoleUpdate) -> dict:
        return data.model_dump(
            include=RoleMapper.UPDATE_FIELDS,
            exclude_unset = True,
        )

    @staticmethod
    def to_list_entity(data: Role) -> RoleList:
        return RoleList.model_validate(data)

    @staticmethod
    def to_read_entity(data: Role) -> RoleRead:
        return RoleRead.model_validate(data)