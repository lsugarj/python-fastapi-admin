import pytest

import app.db.session as db_session


class _Settings:
    class _DB:
        mysql_url = "mysql+asyncmy://u:p@h:3306/db?charset=utf8mb4"
        echo = False
        pool_size = 3
        max_overflow = 4
        pool_timeout = 5
        pool_recycle = 6

    database = _DB()


class _FakeEngine:
    def __init__(self):
        self.disposed = False

    async def dispose(self):
        self.disposed = True


class _FakeBeginCM:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def begin(self):
        return _FakeBeginCM()


class _FakeSessionCM:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


def _fake_sessionmaker(*, bind, expire_on_commit, autoflush):
    def _factory():
        return _FakeSessionCM(_FakeSession())

    return _factory


@pytest.mark.asyncio
async def test_get_engine_raises_before_init():
    await db_session.close_engine()
    with pytest.raises(RuntimeError):
        db_session.get_engine()


@pytest.mark.asyncio
async def test_init_engine_sets_engine_and_session_factory(monkeypatch):
    await db_session.close_engine()

    created = {}

    def fake_create_async_engine(url, **kwargs):
        created["url"] = url
        created["kwargs"] = kwargs
        return _FakeEngine()

    monkeypatch.setattr(db_session, "get_settings", lambda: _Settings())
    monkeypatch.setattr(db_session, "create_async_engine", fake_create_async_engine)
    monkeypatch.setattr(db_session, "async_sessionmaker", _fake_sessionmaker)

    await db_session.init_engine()

    assert created["url"] == _Settings.database.mysql_url
    assert created["kwargs"]["echo"] is False
    assert created["kwargs"]["pool_size"] == 3
    assert created["kwargs"]["max_overflow"] == 4
    assert created["kwargs"]["pool_timeout"] == 5
    assert created["kwargs"]["pool_recycle"] == 6

    engine = db_session.get_engine()
    assert isinstance(engine, _FakeEngine)

    sessions = []
    async for s in db_session.get_session():
        sessions.append(s)
    assert len(sessions) == 1

    read_sessions = []
    async for s in db_session.get_read_session():
        read_sessions.append(s)
    assert len(read_sessions) == 1


@pytest.mark.asyncio
async def test_close_engine_disposes(monkeypatch):
    await db_session.close_engine()

    fake_engine = _FakeEngine()
    monkeypatch.setattr(db_session, "_engine", fake_engine, raising=False)

    await db_session.close_engine()
    assert fake_engine.disposed is True
    assert db_session._engine is None
