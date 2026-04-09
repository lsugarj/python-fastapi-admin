from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer, SmallInteger, UniqueConstraint, Index
from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_role",
        lazy="noload"
    )
    __table_args__ = (
        UniqueConstraint("username", name="uk_user_username"),
        Index("idx_user_deleted_at", "deleted_at"),
    )


class Role(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="role_permission",
        lazy="noload"
    )
    __table_args__ = (
        UniqueConstraint("code", name="uk_role_code"),
        Index("idx_role_deleted_at", "deleted_at"),
    )


class Permission(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限标识，如 user:add")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    path: Mapped[str] = mapped_column(String(256), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    __table_args__ = (
        UniqueConstraint("code", name="uk_permission_code"),
        Index("idx_permission_deleted_at", "deleted_at"),
    )


class Menu(Base, TimestampMixin):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, comment="1: 目录，2: 菜单，3: 按钮")
    icon: Mapped[str] = mapped_column(String(64), nullable=True)
    path: Mapped[str] = mapped_column(String(128), nullable=True)
    sort: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permission.id"),
        nullable=True,
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        lazy="noload"
    )
    __table_args__ = (
        UniqueConstraint("code", name="uk_menu_code"),
    )


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    __table_args__ = (
        Index("idx_user_role_user_id", "user_id"),
        Index("idx_user_role_role_id", "role_id"),
    )



class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), primary_key=True)
    __table_args__ = (
        Index("idx_role_permission_role_id", "role_id"),
        Index("idx_role_permission_permission_id", "permission_id"),
    )