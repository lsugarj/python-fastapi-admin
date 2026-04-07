import pytest

from app.core.redis import RedisClient


class _RedisConfig:
    host = "localhost"
    port = 6379
    db = 0


class _Settings:
    redis = _RedisConfig()


class _FakeRedis:
    def __init__(self, *, ping_raises: Exception | None = None, close_raises: Exception | None = None):
        self._ping_raises = ping_raises
        self._close_raises = close_raises
        self.ping_called = 0
        self.close_called = 0

    async def ping(self):
        self.ping_called += 1
        if self._ping_raises:
            raise self._ping_raises
        return True

    async def close(self):
        self.close_called += 1
        if self._close_raises:
            raise self._close_raises
        return True


@pytest.mark.asyncio
async def test_redis_init_success_and_idempotent(monkeypatch):
    RedisClient._client = None

    fake = _FakeRedis()

    class _RedisFactory:
        @staticmethod
        def from_url(url, encoding, decode_responses):
            assert url == "redis://localhost:6379/0"
            assert encoding == "utf-8"
            assert decode_responses is True
            return fake

    monkeypatch.setattr("app.core.redis.get_settings", lambda: _Settings())
    monkeypatch.setattr("app.core.redis.Redis", _RedisFactory)

    await RedisClient.init()
    assert RedisClient.get_client() is fake
    assert fake.ping_called == 1

    await RedisClient.init()
    assert fake.ping_called == 1

    await RedisClient.close()
    assert RedisClient._client is None
    assert fake.close_called == 1


@pytest.mark.asyncio
async def test_redis_init_failure_raises(monkeypatch):
    RedisClient._client = None

    fake = _FakeRedis(ping_raises=RuntimeError("boom"))

    class _RedisFactory:
        @staticmethod
        def from_url(url, encoding, decode_responses):
            return fake

    monkeypatch.setattr("app.core.redis.get_settings", lambda: _Settings())
    monkeypatch.setattr("app.core.redis.Redis", _RedisFactory)

    with pytest.raises(RuntimeError, match="Redis 初始化失败"):
        await RedisClient.init()
    assert RedisClient._client is fake

    await RedisClient.close()
    assert RedisClient._client is None


def test_get_client_before_init_raises():
    RedisClient._client = None
    with pytest.raises(RuntimeError):
        RedisClient.get_client()


@pytest.mark.asyncio
async def test_close_ignores_close_errors(monkeypatch):
    RedisClient._client = _FakeRedis(close_raises=RuntimeError("close-fail"))
    await RedisClient.close()
    assert RedisClient._client is None
