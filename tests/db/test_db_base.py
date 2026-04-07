from datetime import UTC

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin


class _Thing(Base, SoftDeleteMixin):
    __tablename__ = "test_soft_delete_mixin_thing"

    id: Mapped[int] = mapped_column(primary_key=True)


def test_soft_delete_mixin():
    obj = _Thing(id=1)
    assert obj.is_deleted is False

    obj.soft_delete()
    assert obj.is_deleted is True
    assert obj.deleted_at is not None
    assert obj.deleted_at.tzinfo == UTC

    obj.restore()
    assert obj.is_deleted is False
    assert obj.deleted_at is None
