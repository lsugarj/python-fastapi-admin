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
        lazy="noload"
    )


class Role(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    menus: Mapped[list["Menu"]] = relationship(
        "Menu",
        secondary="role_menu",
        lazy="noload"
    )


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)



class RoleMenu(Base):
    __tablename__ = "role_menu"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), primary_key=True)


class Permission(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, comment="权限标识，如 user:add")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    path: Mapped[str] = mapped_column(String(255), nullable=True)
    method: Mapped[str] = mapped_column(String(10), nullable=True)
    def __repr__(self):
        return f"<Permission {self.name}>"


class Menu(Base, TimestampMixin):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    icon: Mapped[str] = mapped_column(String(64))
    path: Mapped[str] = mapped_column(String(128))
    sort: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # 外键
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("permission.id"),
        default=0,
        nullable=True
    )
    # ORM 关系（关键）
    permission: Mapped["Permission"] = relationship(
        "Permission",
        lazy="noload"
    )
    # 树结构
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("menu.id"),
        nullable=True
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