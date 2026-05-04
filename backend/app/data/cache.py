"""Redis 缓存"""
import redis
from app.config import get_settings

_client = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        settings = get_settings()
        try:
            _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _client.ping()
        except Exception:
            _client = None  # Redis 不可用时降级
    return _client


def cache_set(key: str, value: str, ttl: int = 3600):
    """写入缓存"""
    client = get_redis()
    if client:
        client.setex(key, ttl, value)


def cache_get(key: str) -> str | None:
    """读取缓存"""
    client = get_redis()
    if client:
        return client.get(key)
    return None
