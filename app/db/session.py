from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 导入触发事件注册
import app.db.filters  # noqa

from app.core.config import get_settings

# 全局单例（应用级资源）
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_engine() -> None:
    """
    初始化数据库引擎（在 FastAPI lifespan 启动时调用）
    """
    global _engine, _session_factory

    if _engine is not None:
        return  # 防止重复初始化

    settings = get_settings()

    _engine = create_async_engine(
        settings.database.mysql_url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
        pool_recycle=settings.database.pool_recycle,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        autoflush=False,
    )


def get_engine() -> AsyncEngine:
    """
    获取 engine（必须在 init_engine 之后调用）
    """
    if _engine is None:
        raise RuntimeError("Engine not initialized. Call init_engine() first.")
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    获取 session factory
    """
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized.")
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入使用的 session（单请求单事务）
    """
    session_factory = _get_session_factory()

    async with session_factory() as session:
        async with session.begin():  # 统一事务入口（自动 commit / rollback）
            yield session


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """
    只读 session（无事务，适用于查询接口）
    """
    session_factory = _get_session_factory()

    async with session_factory() as session:
        yield session


async def close_engine() -> None:
    """
    关闭数据库连接池（在 FastAPI shutdown 时调用）
    """
    global _engine

    if _engine is not None:
        await _engine.dispose()
        _engine = None