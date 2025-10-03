from typing import Dict, List
from pathlib import Path
from storage.cache import LRUCache
from storage.bloom_filter import BloomFilter
import storage.binary_handler as binary_handler
from functools import wraps


def count_operations(func):
    """Декоратор, который увеличивает _operation_count на 1, если is_compact
    равен True"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if not self.is_compact:
            self._operation_count += 1
        if self._operation_count >= self._compact_threshold:
            self._compact()
        return result

    return wrapper


class KVStorage:
    def __init__(self, storage_name: str, storage_dir: str = "disk",
                 cache_size: int = 200000):
        if cache_size <= 0:
            raise ValueError("Cache size must be greater than zero")

        self.storage_dir = Path(storage_dir)
        self.storage_path = self.storage_dir / f"{storage_name}.bin"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.touch()

        self.cache_size = cache_size
        self._cache = LRUCache(capacity=cache_size)
        self.bloom_filter = BloomFilter(size=cache_size)

        self.compact_signal = cache_size * 2
        self.deleted_counter = 0

        self.is_compact = True
        self._compact_threshold = 500
        self._operation_count = 0

        self._rebuild_bloom_filter()
        self._load_cache()
        self._compact()

    def _iter_records(self):
        if not self.storage_path.exists():
            return
        with (open(self.storage_path, "rb") as file):
            position = 0
            while True:
                key, value, next_pos = binary_handler.read_record(file,
                                                                  position)
                if key is None:
                    break
                yield key, value, position
                position = next_pos

    def _load_cache(self) -> None:
        for key, value, position in self._iter_records():
            if len(value) > 0:
                self._cache.put(key, position)

    def _compact(self) -> None:
        latest_positions: Dict[str, int] = {}
        for key, _, position in self._iter_records():
            latest_positions[key] = position

        temp_path = self.storage_path.with_suffix(".tmp")
        temp_path.touch()

        with open(temp_path, "ab") as tmp_file:
            for key, value, position in self._iter_records():
                if latest_positions.get(key) == position and len(value) > 0:
                    binary_handler.write_record(tmp_file, key, value)

        temp_path.replace(self.storage_path)

        self.is_compact = True
        self._operation_count = 0
        self._cache.clear()
        self._load_cache()
        self._rebuild_bloom_filter()

    def _rebuild_bloom_filter(self):
        self.bloom_filter.clear()

        latest_positions: Dict[str, int] = {}
        for key, _, position in self._iter_records():
            latest_positions[key] = position

        for key, value, position in self._iter_records():
            if latest_positions.get(key) == position and len(value) > 0:
                self.bloom_filter.add_to_filter(key)

    def _get_from_cache(self, key: str) -> bytes | None:
        position = self._cache.get(key)
        if position is None:
            return None
        with open(self.storage_path, 'rb') as file:
            stored_key, value, _ = binary_handler.read_record(file, position)
        if stored_key == key:
            return value
        return None

    def _get_from_binary_slow(self, key: str):
        last_value = None
        found_position = 0
        for key_data, value, position in self._iter_records():
            if key_data == key:
                last_value = value
                found_position = position
        if last_value is not None and len(last_value) > 0:
            self._cache.put(key, found_position)
            return last_value
        return None

    def _get_from_binary_fast(self, key: str):
        for key_data, value, position in self._iter_records():
            if key_data == key:
                self._cache.put(key, position)
                return value
        return None

    @count_operations
    def get(self, key: str) -> bytes | None:
        if self.bloom_filter.is_not_presented(key):
            return None
        value = self._get_from_cache(key)
        if value:
            return value
        if not self.is_compact:
            return self._get_from_binary_slow(key)
        return self._get_from_binary_fast(key)

    @count_operations
    def add(self, key: str, value: bytes) -> None:
        position = binary_handler.write_to_file(self.storage_path, key, value)
        self._cache.put(key, position)
        self.bloom_filter.add_to_filter(key)

    def add_many(self, items: Dict[str, bytes]) -> None:
        for key, value in items.items():
            self.add(key, value)

    @count_operations
    def delete(self, key: str) -> None:
        self._cache.delete(key)
        binary_handler.write_to_file(self.storage_path, key, b"")
        self.deleted_counter += 1
        if self.deleted_counter == self.compact_signal:
            self._compact()
            self.deleted_counter = 0
        self.is_compact = False

    def keys(self) -> List[str]:
        return list(binary_handler.all_keys(self.storage_path))

    def clear(self) -> None:
        with open(self.storage_path, 'rb+') as f:
            f.truncate(0)
        self._cache.clear()
        self.bloom_filter.clear()
