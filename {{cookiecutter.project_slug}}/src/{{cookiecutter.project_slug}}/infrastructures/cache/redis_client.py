{% if cookiecutter.use_cache in ["redis", "keydb", "dragonfly"] %}
from dataclasses import dataclass
import json
from typing import Any, final

import structlog
from redis.asyncio import Redis
import redis.exceptions

from {{cookiecutter.project_slug}}.application.interfaces.cache import CacheProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CacheClient(CacheProtocol):
    """Redis-protocol cache client (supports Redis, KeyDB, Dragonfly)."""

    client: Redis
    ttl: int | None = None

    async def get(self, key: str) -> dict[str, Any] | None:
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Failed to decode cached value", key=key, error=str(e))
            return None

    async def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> bool:
        try:
            serialized = json.dumps(value, default=str)
            effective_ttl = ttl if ttl is not None else self.ttl
            if effective_ttl is not None:
                await self.client.setex(key, effective_ttl, serialized)
            else:
                await self.client.set(key, serialized)
            return True
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
        except (TypeError, ValueError) as e:
            logger.error("Failed to serialize value for cache", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        try:
            return await self.client.delete(key) > 0
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.client.exists(key))
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Cache exists failed", key=key, error=str(e))
            return False

    async def clear(self, pattern: str) -> int:
        try:
            keys = [key async for key in self.client.scan_iter(match=pattern)]
            if not keys:
                return 0
            deleted = await self.client.delete(*keys)
            logger.info("Cleared cache keys", pattern=pattern, count=deleted)
            return deleted
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Cache clear failed", pattern=pattern, error=str(e))
            return 0

    async def close(self) -> None:
        try:
            await self.client.aclose()
        except (ConnectionError, redis.exceptions.RedisError) as e:
            logger.error("Failed to close cache connection", error=str(e))


# Backwards-compatible alias.
RedisCacheClient = CacheClient
{% else %}
from dataclasses import dataclass
from typing import Any, final

import structlog

from {{cookiecutter.project_slug}}.application.interfaces.cache import CacheProtocol

logger = structlog.get_logger(__name__)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class CacheClient(CacheProtocol):
    """No-op cache client (used when no cache backend is configured{% if cookiecutter.use_cache == "tarantool" %}, or for Tarantool which is not yet implemented{% endif %})."""

    async def get(self, key: str) -> dict[str, Any] | None:
        return None

    async def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> bool:
        return True

    async def delete(self, key: str) -> bool:
        return True

    async def exists(self, key: str) -> bool:
        return False

    async def clear(self, pattern: str) -> int:
        return 0

    async def close(self) -> None:
        pass


RedisCacheClient = CacheClient
{% endif %}
