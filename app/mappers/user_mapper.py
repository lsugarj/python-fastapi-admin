from app.models.rbac import User
from app.schemas.user import UserCreate, UserUpdate, UserList, UserRead, CurrentUser


class UserMapper:

    CREATE_FIELDS = {"username", "password", "email", "phone"}
    UPDATE_FIELDS = {"email", "phone", "is_active"}

    @staticmethod
    def to_create_entity(data: UserCreate) -> User:
        return User(**data.model_dump(include=UserMapper.CREATE_FIELDS))


    @staticmethod
    def to_update_dict(data: UserUpdate) -> dict:
        return data.model_dump(
            include=UserMapper.UPDATE_FIELDS,
            exclude_unset = True,
        )

    @staticmethod
    def to_list_entity(data: User) -> UserList:
        return UserList.model_validate(data)

    @staticmethod
    def to_read_entity(data: User) -> UserRead:
        return UserRead.model_validate(data)

    @staticmethod
    def to_current_user_entity(user: User) -> CurrentUser:
        data = CurrentUser(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            token_version=user.token_version,
            is_active=user.is_active,
            roles=[r.code for r in user.roles]
        )
        return data