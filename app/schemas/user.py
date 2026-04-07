from datetime import datetime
from pydantic import EmailStr, computed_field, ConfigDict
from app.schemas.common import PageParamsRequestBaseModel, RequestBaseModel, ResponseBaseModel
from app.schemas.role import RoleRead


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
    roles: list[str]

class UserCreate(RequestBaseModel):
    username: str
    password: str
    email: EmailStr
    phone: str
    role_ids: list[int] | None = []

class UserUpdate(RequestBaseModel):
    email: EmailStr
    phone: str
    is_active: bool
    role_ids: list[int] | None = []

class UserList(ResponseBaseModel):
    id: int
    username: str
    email: str

class UserRead(ResponseBaseModel):
    id: int
    username: str
    email: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserPage(UserRead):
    roles: list[RoleRead]

class UserPageQueryParams(PageParamsRequestBaseModel):
    username: str | None = None
    is_active: bool | None = None