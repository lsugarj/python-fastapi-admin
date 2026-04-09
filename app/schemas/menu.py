from datetime import datetime
from app.schemas.common import ResponseBaseModel, RequestBaseModel, PageParamsRequestBaseModel
from app.schemas.permission import PermissionList


class MenuCreate(RequestBaseModel):
    code: str
    name: str
    type: int
    icon: str
    path: str
    sort: int = 0
    is_visible: bool = True
    parent_id: int | None = None
    permission_id: int | None = None

class MenuUpdate(RequestBaseModel):
    code: str | None = None
    name: str | None = None
    type: int | None = None
    icon: str | None = None
    path: str | None = None
    sort: int | None = None
    is_visible: bool | None = None
    parent_id: int | None = None
    permission_id: int | None = None

class MenuList(ResponseBaseModel):
    id: int
    code: str
    name: str
    type: int
    icon: str | None
    path: str | None
    sort: int
    is_visible: bool
    parent_id: int | None

class MenuRead(MenuList):
    permission_id: int | None
    permission: PermissionList | None
    created_at: datetime
    updated_at: datetime

class MenuPageQueryParams(PageParamsRequestBaseModel):
    name: str | None = None
    path: str | None = None
