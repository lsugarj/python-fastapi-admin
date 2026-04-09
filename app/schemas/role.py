from datetime import datetime
from pydantic import Field
from app.schemas.common import RequestBaseModel, PageParamsRequestBaseModel, ResponseBaseModel
from app.schemas.permission import PermissionList


class RoleCreate(RequestBaseModel):
    code: str
    name: str
    is_active: bool = True
    permission_ids: list[int] = Field(default_factory=list)

class RoleUpdate(RequestBaseModel):
    name: str | None = None
    is_active: bool | None = None
    permission_ids: list[int] | None = None

class RoleList(ResponseBaseModel):
    id: int
    code: str
    name: str

class RoleRead(RoleList):
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionList]

class RolePageQueryParams(PageParamsRequestBaseModel):
    code: str | None = None
    name: str | None = None
