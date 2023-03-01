from typing import Optional, Any

from cachetools import TTLCache


class Cache:
    """LRU Cache implementation with per-item time-to-live (TTL) for storing request data."""

    def __init__(self, max_cache_size: float, ttl: float) -> None:
        """Inits Cache with the cache_size and TTL.

        Args:
            max_cache_size: Maximum cache size.
            ttl: Time to live in seconds for each item.
        """
        self.data = TTLCache(maxsize=max_cache_size, ttl=ttl)

    def get_data(self, hash_: int) -> Optional[Any]:
        """Gets the cached data.

        Args:
            hash_: Band signature hash.

        Returns:
            The associated data if it exists. If not, returns None.
        """
        return self.data.get(hash_, None)

    def set_data(self, hash_: int, data: Any) -> None:
        """Sets the data to the cache.

        Args:
            hash_: Band signature hash.
            data: Associated data to store alongside the hash.
        """
        self.data[hash_] = data
