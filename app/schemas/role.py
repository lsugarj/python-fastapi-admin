from datetime import datetime
from app.schemas.common import RequestBaseModel, PageParamsRequestBaseModel, ResponseBaseModel
from app.schemas.menu import MenuList


class RoleCreate(RequestBaseModel):
    code: str
    name: str
    is_active: bool | None = True
    menu_ids: list[int] | None = []

class RoleUpdate(RoleCreate):
    name: str
    menu_ids: list[int] | None = []

class RoleList(ResponseBaseModel):
    id: int
    code: str
    name: str

class RoleRead(RoleList):
    created_at: datetime
    updated_at: datetime
    menus: list[MenuList]

class RolePage(RoleList):
    created_at: datetime
    updated_at: datetime

class RolePageQueryParams(PageParamsRequestBaseModel):
    code: str | None = None
    name: str | None = None