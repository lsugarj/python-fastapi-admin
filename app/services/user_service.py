from typing import List
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.models.rbac import User
from app.repositorys.user_repo import UserRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserPageQueryParams, UserList, UserPage, CurrentUser
from app.exceptions.business import AuthException
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserLogin


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:

    @staticmethod
    async def login(data: UserLogin, session: AsyncSession):
        user = await UserRepository.get_user_for_login(data.username, session)
        if not user or not verify_password(data.password, user.password):
            raise AuthException(Code.LOGIN_FAILED, "用户名或密码错误")
        if not user.is_active:
            raise AuthException(Code.LOGIN_FAILED, "用户被禁用，请联系管理员")
        # 单点登录核心
        token_version = user.token_version + 1
        is_success = await UserRepository.update_user_token_version(user.id, token_version, session)
        if not is_success:
            raise AuthException(Code.LOGIN_FAILED, "登陆失败，请联系管理员或稍后重试")
        token = create_access_token({"sub": user.id}, token_version)
        return user.id, token


    @staticmethod
    async def logout(user_id: int, session: AsyncSession) -> BoolResult:
        # 修改token version + 1
        user = await UserRepository.get_user_by_id(user_id, session)
        if not user:
            raise AuthException(Code.LOGOUT_FAILED, "操作失败，请联系管理员或稍后重试")
        # 单点登录核心
        token_version = user.token_version + 1
        is_success = UserRepository.update_user_token_version(user_id, token_version, session)
        if not is_success:
            raise AuthException(Code.LOGIN_FAILED, "操作失败，请联系管理员或稍后重试")
        return BoolResult(success=True)

    @staticmethod
    async def get_current_user(user_id: int, session: AsyncSession) -> CurrentUser | None:
        user = await UserRepository.get_current_user(user_id, session)
        if not user:
            return None
        data = CurrentUser(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            token_version=user.token_version,
            roles=[r.code for r in user.roles]
        )
        return data


    @staticmethod
    async def create_user(data: UserCreate, session: AsyncSession) -> IDResult:
        existing = await UserRepository.exists_by_username(data.username, session)
        if existing:
            raise BusinessException(Code.USER_ALREADY_EXISTS, "用户已经存在")
        hashed_password = pwd_context.hash(data.password)
        user = User(username=data.username, password=hashed_password, email=data.email, phone=data.phone)
        user_id = await UserRepository.create_user(user, data.role_ids, session)
        return IDResult(id=user_id)


    @staticmethod
    async def update_user(user_id: int, data: UserUpdate, session: AsyncSession) -> BoolResult:
        # 提取更新字段
        update_data = data.model_dump(exclude_unset=True, exclude={"role_ids"})
        if not update_data:
            return BoolResult(success=False)
        # 直接 UPDATE
        is_success = await UserRepository.update_user(user_id, update_data, data.role_ids, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await UserRepository.exists(user_id, session)
        if not exists:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        # 存在但没更新成功
        return BoolResult(success=False)


    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> BoolResult:
        # 直接 UPDATE
        is_success = await UserRepository.delete_user(user_id, session)
        # 如果更新成功
        if is_success:
            return BoolResult(success=True)
        # 失败 → 补查（区分不存在 vs 幂等）
        exists = await UserRepository.exists(user_id, session)
        if not exists:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        # 存在但没删除成功
        return BoolResult(success=False)


    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserRead | None:
        user = await UserRepository.get_user_by_id(user_id, session)
        if not user:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        return UserRead.model_validate(user) if user else None


    @staticmethod
    async def get_user_by_name(username: str, session: AsyncSession) -> UserRead | None:
        user = await UserRepository.get_user_by_username(username, session)
        if not user:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        return UserRead.model_validate(user) if user else None


    @staticmethod
    async def get_user_list(session: AsyncSession) -> List[UserList]:
        users = await UserRepository.get_user_list(session)
        items = [
            UserList.model_validate(u) for u in users
        ]
        return items


    @staticmethod
    async def get_user_page(params: UserPageQueryParams, session: AsyncSession) -> PageResult[UserPage]:
        total, users = await UserRepository.get_user_page(params, session)
        items = [
            UserPage.model_validate(u) for u in users
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )