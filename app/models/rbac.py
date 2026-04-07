from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer, SmallInteger
from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_role",
        back_populates="users",
        lazy="selectin"
    )


class Role(Base, TimestampMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name = mapped_column(String(64), nullable=False)
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_role",
        back_populates="roles",
        lazy="selectin"
    )


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class RoleMenu(Base):
    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), primary_key=True)

class Permission(Base, TimestampMixin):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, comment="权限标识，如 user:add")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    def __repr__(self):
        return f"<Permission {self.name}>"


class Menu(Base, TimestampMixin):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(64), nullable=False, comment="菜单名称")
    label_en: Mapped[str] = mapped_column(String(64), nullable=False, comment="菜单名称")
    type: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="0目录 1菜单 2按钮")
    icon: Mapped[str] = mapped_column(String(64), comment="图标")
    path: Mapped[str] = mapped_column(String(128), comment="路由路径")
    sort: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="排序")
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否显示")
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), default=0, nullable=False, comment="权限ID")
    permission: Mapped[str] = mapped_column(
        String(128),
        comment="权限标识"
    )
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("menu.id"),
        nullable=True,
        comment="父菜单ID"
    )
    parent: Mapped["Menu"] = relationship(
        "Menu",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Menu"]] = relationship(
        "Menu",
        back_populates="parent",
        cascade="all, delete-orphan"
    )