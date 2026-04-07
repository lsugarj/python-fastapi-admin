import json
import inspect
from typing import Any, Type, Callable, Coroutine
from pydantic import BaseModel
from app.core.redis import RedisClient


__NULL__ = "__NULL__"


class RedisCache:
    """
    Redis 缓存工具类
    """

    @staticmethod
    async def set(key: str, value: Any, expire: int | None = None):
        redis = RedisClient.get_client()

        if not isinstance(value, str):
            if isinstance(value, BaseModel):
                value = json.dumps(value.model_dump())
            else:
                value = json.dumps(value)

        await redis.set(key, value, ex=expire)


    @staticmethod
    async def get(key: str) -> Any:
        redis = RedisClient.get_client()
        value = await redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return value


    @staticmethod
    async def delete(key: str):
        redis = RedisClient.get_client()
        await redis.delete(key)


    @staticmethod
    async def exists(key: str) -> bool:
        redis = RedisClient.get_client()
        return await redis.exists(key) > 0


    @staticmethod
    async def expire(key: str, seconds: int):
        redis = RedisClient.get_client()
        await redis.expire(key, seconds)


def redis_cache(
    *,
    model: Type[BaseModel],
    key_builder: Callable[..., str],
    expire: int = 60
) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
    """
    Redis 缓存装饰器

    - model: 返回值模型，用于反序列化
    - key_builder: 根据函数参数生成缓存 key 的方法
    - expire: 缓存过期时间
    """

    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:

        async def wrapper(*args, **kwargs):
            # 参数绑定（关键）
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            key = key_builder(**bound.arguments)
            cache = await RedisCache.get(key)

            if cache is not None:
                if cache == __NULL__:
                    return None
                if isinstance(cache, (str, bytes)):
                    data = json.loads(cache)
                else:
                    data = cache
                return model.model_validate(data)

            # 调用原函数
            result = await func(*args, **kwargs)

            # 缓存空值（防穿透）
            if result is None:
                await RedisCache.set(key, __NULL__, expire=expire)
                return None

            # 缓存实际数据
            await RedisCache.set(
                key,
                result.model_dump(),
                expire=expire
            )

            return result

        return wrapper

    return decorator