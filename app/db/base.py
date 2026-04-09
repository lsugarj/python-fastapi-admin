from datetime import datetime, UTC
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData, DateTime, func


class Base(DeclarativeBase):
    # 统一命名规则（非常重要，Alembic 不会乱 diff）
    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s",
            "uq": "uk_%(table_name)s_%(column_0_name)s",
            "ix": "idx_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
        }
    )

# =========================
# 时间字段 Mixin
# =========================
class TimestampMixin:
    """
    自动维护创建时间 / 更新时间
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# =========================
# 软删除 Mixin
# =========================
class SoftDeleteMixin:
    """
    软删除支持
    """
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    def soft_delete(self):
        self.deleted_at = datetime.now(UTC)

    def restore(self):
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None