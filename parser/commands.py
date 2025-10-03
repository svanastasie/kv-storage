import argparse
import sys
import os
from storage.storage import KVStorage
from parser.file_handler import read_txt_file


def encode_value(value: str) -> bytes | None:
    return value.encode("utf-8")


def decode_value(value_data: bytes):
    return value_data.decode("utf-8")


def validate_storage_name(name: str) -> None:
    if not name or not isinstance(name, str):
        print("Error: Storage name must be a non-empty string")
        sys.exit(1)
    if any(c in name for c in r'\/:*?"<>|'):
        print("Error: Storage name contains invalid characters")
        sys.exit(1)


def validate_key(key: str) -> None:
    if not key or not isinstance(key, str):
        print("Error: Key must be a non-empty string")
        sys.exit(1)


def handle_command(args: argparse.Namespace, storage: KVStorage) -> None:
    commands = {'add': handle_add, 'add-many': handle_add_many,
                'get': handle_get, 'delete': handle_delete,
                'keys': handle_keys, 'clear': handle_clear}

    handler = commands.get(args.command)
    if handler:
        handler(args, storage)
    else:
        print(f"Unknown command: {args.command}")


def handle_add(args, storage: KVStorage) -> None:
    validate_key(args.key)
    value = encode_value(args.value)
    storage.add(args.key, value)
    print(f"Stored {args.key}")


def handle_add_many(args, storage: KVStorage) -> None:
    if args.file:
        if not os.path.isfile(args.file):
            print(f"File not found: {args.file}")
            return
        try:
            data = read_txt_file(args.file)
            encoded_data = {k: encode_value(v) for k, v in data.items()}
            storage.add_many(encoded_data)
            print(f"Successfully added {len(data)} key-value pairs from file")
        except Exception as e:
            print(f"Error adding data.txt from file: {e}")

    elif args.interactive:
        print("Enter key-value pairs separated by comma:")
        print("(Empty string completes the input)")
        while True:
            line = input()
            if not line.strip():
                break
            parts = line.strip().split(",")
            if len(parts) != 2:
                print("Please enter a key and value separated by comma")
                continue
            key, value = parts
            storage.add(key, encode_value(value))
        print("Data is successfully stored")


def handle_get(args, storage: KVStorage) -> None:
    validate_key(args.key)
    value = storage.get(args.key)
    if value is None:
        print(f"Key '{args.key}' not found")
        return
    decoded_value = decode_value(value)
    print(decoded_value)


def handle_delete(args, storage: KVStorage) -> None:
    validate_key(args.key)
    if storage.delete(args.key):
        print(f"Deleted {args.key}")
    else:
        print(f"Key '{args.key}' not found")


def handle_keys(storage: KVStorage) -> None:
    keys = storage.keys()
    if not keys:
        print("Storage is empty")
    else:
        print(f"Total keys: {len(keys)}")
        print("\n".join(keys))


def handle_clear(storage: KVStorage) -> None:
    confirm = (input(
        "Are you sure you want to clear all data.txt? [yes/no] ").lower())
    if confirm == 'yes':
        storage.clear()
        print("Storage cleared")
    else:
        print("Operation cancelled")
