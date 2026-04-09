from app.models.rbac import Menu
from app.schemas.menu import MenuCreate, MenuUpdate, MenuList, MenuRead


class MenuMapper:

    CREATE_FIELDS = {"code", "name", "type", "icon", "path", "sort", "is_visible", "permission_id", "parent_id"}

    @staticmethod
    def to_create_entity(data: MenuCreate) -> Menu:
        return Menu(**data.model_dump(include=MenuMapper.CREATE_FIELDS))


    @staticmethod
    def to_update_dict(data: MenuUpdate) -> dict:
        return data.model_dump(
            include=MenuMapper.CREATE_FIELDS,
            exclude_unset=True
        )

    @staticmethod
    def to_list_entity(data: Menu) -> MenuList:
        return MenuList.model_validate(data)

    @staticmethod
    def to_read_entity(data: Menu) -> MenuRead:
        return MenuRead.model_validate(data)