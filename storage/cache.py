import hashlib
from collections import OrderedDict


class LRUCache:
    """LRU cache, based on Ordered Dict"""

    def __init__(self, capacity: int, max_key_len: int = 10000):
        if capacity < 0:
            raise ValueError("Capacity must be greater than 0")
        self.capacity = capacity
        self.max_key_len = max_key_len
        self._cache = OrderedDict()

    @staticmethod
    def _get_hash(key: str) -> int:
        h_bytes = hashlib.sha256(key.encode("utf-8")).digest()
        return int.from_bytes(h_bytes, byteorder="big")

    def _normalize_key(self, key: str) -> str | int:
        if len(key) <= self.max_key_len:
            return key
        return self._get_hash(key)

    def get(self, key):
        norm_key = self._normalize_key(key)
        if norm_key in self._cache:
            self._cache.move_to_end(norm_key)
            return self._cache[norm_key]
        return None

    def put(self, key: str, pointer: int) -> None:
        norm_key = self._normalize_key(key)
        if norm_key in self._cache:
            self._cache.move_to_end(norm_key)
        elif len(self._cache) == self.capacity:
            self._cache.popitem(last=False)
        self._cache[norm_key] = pointer

    def delete(self, key):
        norm_key = self._normalize_key(key)
        if norm_key in self._cache:
            del self._cache[norm_key]

    def clear(self):
        self._cache.clear()
