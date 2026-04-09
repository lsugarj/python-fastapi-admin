from typing import List
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException
from app.mappers.user_mapper import UserMapper
from app.repositorys.user_repo import UserRepository
from app.schemas.common import PageResult, IDResult, BoolResult
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserPageQueryParams, UserList, CurrentUser
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
    async def get_current_user(user_id: int, session: AsyncSession) -> CurrentUser:
        user = await UserRepository.get_current_user(user_id, session)
        if not user:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        data = UserMapper.to_current_user_entity(user)
        return data


    @staticmethod
    async def create_user(data: UserCreate, session: AsyncSession) -> IDResult:
        existing = await UserRepository.exists_by_username(data.username, session)
        if existing:
            raise BusinessException(Code.USER_ALREADY_EXISTS, "用户已经存在")
        hashed_password = pwd_context.hash(data.password)
        data.password = hashed_password
        # DTO → Entity
        user = UserMapper.to_create_entity(data)
        user_id = await UserRepository.create_user(user, data.role_ids, session)
        return IDResult(id=user_id)


    @staticmethod
    async def update_user(user_id: int, data: UserUpdate, session: AsyncSession) -> BoolResult:
        # DTO → update dict
        update_data = UserMapper.to_update_dict(data)
        if not update_data:
            return BoolResult(success=False)
        # 执行更新
        is_success = await UserRepository.update_user(user_id, update_data, data.role_ids, session)
        if not is_success:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        return BoolResult(success=True)


    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> BoolResult:
        is_success = await UserRepository.delete_user(user_id, session)
        if not is_success:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        return BoolResult(success=True)


    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserRead:
        user = await UserRepository.get_user_by_id(user_id, session)
        if not user:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        data = UserMapper.to_read_entity(user)
        return data


    @staticmethod
    async def get_user_by_name(username: str, session: AsyncSession) -> UserRead:
        user = await UserRepository.get_user_by_username(username, session)
        if not user:
            raise BusinessException(Code.USER_NOT_FOUND, "用户不存在")
        data = UserMapper.to_read_entity(user)
        return data


    @staticmethod
    async def get_user_list(session: AsyncSession) -> List[UserList]:
        users = await UserRepository.get_user_list(session)
        items = [
            UserMapper.to_list_entity(u) for u in users
        ]
        return items


    @staticmethod
    async def get_user_page(params: UserPageQueryParams, session: AsyncSession) -> PageResult[UserRead]:
        total, users = await UserRepository.get_user_page(params, session)
        items = [
            UserMapper.to_read_entity(u) for u in users
        ]
        return PageResult(
            total=total,
            page=params.page,
            size=params.size,
            items=items,
        )