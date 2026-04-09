from datetime import datetime

from pydantic import field_validator

from app.schemas.common import RequestBaseModel, PageParamsRequestBaseModel, ResponseBaseModel


class PermissionCreate(RequestBaseModel):
    code: str
    name: str
    path: str
    method: str

class PermissionUpdate(RequestBaseModel):
    name: str | None = None
    path: str | None = None
    method: str | None = None

    @field_validator("name", "path", "method")
    @classmethod
    def not_empty(cls, v):
        if v is None:
            return v  # 不传
        if not v.strip():
            raise ValueError("cannot be empty")
        return v

class PermissionList(ResponseBaseModel):
    id: int
    code: str
    name: str

class PermissionRead(PermissionList):
    path: str
    method: str
    created_at: datetime
    updated_at: datetime

class PermissionPageQueryParams(PageParamsRequestBaseModel):
    code: str | None = None
    name: str | None = None
    path: str | None = None
