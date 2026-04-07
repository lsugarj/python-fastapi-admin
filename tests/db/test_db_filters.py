from datetime import datetime, UTC

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin
import app.db.filters  # noqa: F401


class _User(Base, SoftDeleteMixin):
    __tablename__ = "test_users_soft_delete"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


def test_soft_delete_filter_excludes_deleted_by_default():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(
            [
                _User(id=1, name="alive", deleted_at=None),
                _User(id=2, name="deleted", deleted_at=datetime.now(UTC)),
            ]
        )
        session.commit()

        users = session.execute(select(_User).order_by(_User.id)).scalars().all()
        assert [u.id for u in users] == [1]

        users_including_deleted = (
            session.execute(
                select(_User).execution_options(include_deleted=True).order_by(_User.id)
            )
            .scalars()
            .all()
        )
        assert [u.id for u in users_including_deleted] == [1, 2]
