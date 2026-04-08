from datetime import datetime
from app.schemas.common import RequestBaseModel, PageParamsRequestBaseModel, ResponseBaseModel


class PermissionCreate(RequestBaseModel):
    code: str
    name: str
    path: str
    method: str

class PermissionUpdate(RequestBaseModel):
    name: str
    path: str
    method: str

class PermissionList(ResponseBaseModel):
    id: int
    code: str
    name: str

class PermissionRead(PermissionList):
    path: str
    method: str
    created_at: datetime
    updated_at: datetime

class PermissionPage(PermissionRead):
    pass

class PermissionPageQueryParams(PageParamsRequestBaseModel):
    name: str | None = None
    path: str | None = None