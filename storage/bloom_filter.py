import hashlib
from math import log
from bitarray import bitarray


class BloomFilter:
    def __init__(self, size: int, number_exp_elements: int = 100000):
        self.size = size
        self.number_expected_elements = max(number_exp_elements, 1)
        self.bloom_filter = bitarray(size)
        self.bloom_filter.setall(0)
        self.hash_count = max(1, round(
            (self.size / self.number_expected_elements) * log(2)))

    def _hash_djb2(self, s: str) -> int:
        hash_val = 5381
        for x in s:
            hash_val = ((hash_val << 5) + hash_val) + ord(x)
        return hash_val % self.size

    def _hash(self, item: str, k: int) -> int:
        return self._hash_djb2(str(k) + item)

    def add_to_filter(self, key: str) -> None:
        for i in range(self.hash_count):
            index = self._hash(key, i)
            self.bloom_filter[index] = 1

    def _may_contain(self, key: str) -> bool:
        for i in range(self.hash_count):
            index = self._hash(key, i)
            if self.bloom_filter[index] == 0:
                return False
        return True

    def is_not_presented(self, key: str) -> bool:
        return not self._may_contain(key)

    def clear(self):
        self.bloom_filter.setall(0)
