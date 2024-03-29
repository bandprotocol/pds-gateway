import json

from abc import abstractmethod
from typing import Optional, Any

from cachetools import TTLCache
from redis import Redis


class Cache:
    @abstractmethod
    def set(self, key: str | int, value: dict) -> None:
        """Set a value to the cache.

        Args:
            key: Key to set the value to.
            value: Value to set.
        """
        pass

    @abstractmethod
    def get(self, key: str | int) -> Optional[dict]:
        """Get a value from the cache.

        Args:
            key: Key to get the value from.

        Returns:
            Value from the middleware.
        """
        pass


class LocalCache(Cache):
    """A local cache.

    Attributes:
        cache: TTLCache instance to store the data.
    """

    def __init__(self, max_cache_size: float, ttl: float) -> None:
        """Initializes LocalCache with the maximum size and TTL.

        Args:
            max_cache_size: Maximum size.
            ttl: Time to live in seconds for each item.
        """
        self.cache = TTLCache(maxsize=max_cache_size, ttl=ttl)

    def set(self, key: str | int, value: dict) -> None:
        """Sets the cached data.

        Args:
            key: Key to set the value to.
            value: Value to set.
        """
        self.cache[key] = value

    def get(self, key: str | int) -> Optional[dict]:
        """Gets the cached data.

        Args:
            key: Key to get the value from.

        Returns:
            Value from the middleware. None if the key is not found.
        """
        return self.cache.get(key, None)


class RedisCache(Cache):
    """A Redis-based cache.

    Attributes:
        redis: Redis instance to connect with Redis.
        ttl: Time to live in seconds.
    """

    def __init__(self, url: str, port: int = 6379, db: int = 0, ttl: int = 60) -> None:
        """Initializes RedisCache with the Redis URL, port, database, and TTL.

        Args:
            url: Redis URL.
            port: Redis port.
            db: Redis database.
            ttl: Time to live in seconds.
        """
        self.redis = Redis(host=url, port=port, db=db)
        self.ttl = ttl

    def set(self, key: str | int, value: dict) -> None:
        """Set a value to the cache

        Args:
            key: Key to set the value to.
            value: Value to set.
        """
        # Enforce value type to be a dict to prevent error with `json.dump`.
        if not isinstance(value, dict):
            raise TypeError(f"Value must be a dict, not {type(value)}")

        # Convert value type from dict to JSON string before setting to Redis.
        saved = self.redis.set(key, json.dumps(value))
        if saved:
            self.redis.expire(key, self.ttl)

    def get(self, key: str | int) -> Optional[dict]:
        """Get a value from the cache

        Args:
            key: Key to get the value from.

        Returns:
            Value from the middleware. None if the key is not found.
        """
        if value := self.redis.get(key):
            return json.loads(value)

        return None
