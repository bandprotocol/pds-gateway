from cachetools import TTLCache


class Cache:
    def __init__(self, cache_size, ttl_time):
        self.data = TTLCache(maxsize=cache_size, ttl=ttl_time)

    def get_data(self, hash):
        return self.data.get(hash, None)

    def set_data(self, hash, data):
        self.data[hash] = data
