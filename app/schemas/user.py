from datetime import datetime
from pydantic import EmailStr, Field, field_validator
from app.schemas.common import PageParamsRequestBaseModel, RequestBaseModel, ResponseBaseModel
from app.schemas.role import RoleList


class UserLogin(RequestBaseModel):
    username: str
    password: str

class Token(ResponseBaseModel):
    token: str

class CurrentUser(ResponseBaseModel):
    id: int
    username: str
    email: str
    phone: str
    token_version: int
    is_active: bool
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)

class UserCreate(RequestBaseModel):
    username: str
    password: str
    email: EmailStr
    phone: str
    is_active: bool = True
    role_ids: list[int] = Field(default_factory=list)

class UserUpdate(RequestBaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool | None = None
    role_ids: list[int] | None = None

    @field_validator("email", "phone", "is_active")
    @classmethod
    def not_empty(cls, v):
        if v is None:
            return v  # 不传
        if not v.strip():
            raise ValueError("cannot be empty")
        return v

class UserList(ResponseBaseModel):
    id: int
    username: str

class UserRead(UserList):
    email: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleList] = Field(default_factory=list)

class UserPageQueryParams(PageParamsRequestBaseModel):
    username: str | None = None
    is_active: bool | None = None
