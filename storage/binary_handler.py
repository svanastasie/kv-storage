from pathlib import Path
from typing import BinaryIO, Generator


def write_record(file: BinaryIO, key: str, value: bytes) -> None:
    """Writes one key-value pair into binary file"""
    key_bytes = key.encode("utf-8")
    key_size = len(key_bytes)
    value_size = len(value)

    file.write(key_size.to_bytes(4, byteorder='big'))
    file.write(key_bytes)
    file.write(value_size.to_bytes(4, byteorder='big'))
    file.write(value)


def read_record(file: BinaryIO, position: int):
    """Reads one record starting from position. Returns (key, value,
    next_position)"""
    file.seek(position)

    key_size_bytes = file.read(4)
    if not key_size_bytes:
        return None, None, None

    key_size = int.from_bytes(key_size_bytes, byteorder='big')
    key = file.read(key_size).decode("utf-8")
    value_size = int.from_bytes(file.read(4), byteorder='big')
    value = file.read(value_size)

    next_position = position + 4 + key_size + 4 + value_size
    return key, value, next_position


def write_to_file(file_path: Path, key: str, value: bytes) -> int:
    """Writes key-value pair into binary file and returns its position"""
    with open(file_path, 'ab') as file:
        position = file.tell()
        write_record(file, key, value)
    return position


def all_keys(file_path: Path) -> Generator[str, None, None]:
    latest_state = {}

    with open(file_path, "rb") as file:
        position = 0
        while True:
            key, value, next_position = read_record(file, position)
            if key is None:
                break
            latest_state[key] = len(value) > 0
            position = next_position

    for key, exists in latest_state.items():
        if exists:
            yield key
