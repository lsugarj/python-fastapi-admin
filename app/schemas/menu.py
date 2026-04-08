from datetime import datetime

from app.schemas.common import ResponseBaseModel, RequestBaseModel, PageParamsRequestBaseModel
from app.schemas.permission import PermissionRead


class MenuCreate(RequestBaseModel):
    code: str
    name: str
    type: int
    icon: str | None
    path: str | None
    sort: int
    is_visible: bool | None = True
    permission_id: int | None = None

class MenuUpdate(RequestBaseModel):
    name: str
    type: int
    icon: str
    path: str
    sort: int
    is_visible: bool
    permission_id: int | None = None

class MenuList(ResponseBaseModel):
    id: int
    code: str
    name: str

class MenuRead(MenuList):
    type: int
    icon: str | None
    path: str | None
    sort: int
    is_visible: bool
    permission_id: int | None
    created_at: datetime
    updated_at: datetime
    permission: PermissionRead | None

class MenuPage(MenuRead):
    pass

class MenuPageQueryParams(PageParamsRequestBaseModel):
    name: str | None = None
    path: str | None = None