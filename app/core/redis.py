from typing import Optional
import logging

from redis.asyncio import Redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis 异步客户端单例
    """
    _client: Optional[Redis] = None

    @classmethod
    async def init(cls) -> None:
        """
        初始化 Redis 客户端
        """
        if cls._client is not None:
            logger.debug("Redis 已初始化，跳过")
            return

        redis_config = get_settings().redis
        url = f"redis://{redis_config.host}:{redis_config.port}/{redis_config.db}"

        try:
            cls._client = Redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True
            )
            # 测试连接
            await cls._client.ping()
            logger.info("Redis 初始化成功")
        except Exception as e:
            logger.exception("Redis 初始化失败: %s", e)
            raise RuntimeError(f"Redis 初始化失败: {e}") from e

    @classmethod
    def get_client(cls) -> Redis:
        """
        获取 Redis 客户端实例
        """
        if cls._client is None:
            raise RuntimeError("Redis 未初始化，请先调用 RedisClient.init()")
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """
        关闭 Redis 连接
        """
        if cls._client:
            try:
                await cls._client.close()
                logger.info("Redis 已关闭")
            except Exception as e:
                logger.warning("Redis 关闭异常: %s", e)
            finally:
                cls._client = None