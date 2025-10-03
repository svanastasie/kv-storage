import sys
from storage.storage import KVStorage
from parser.arg_parser import parse_args
from parser.commands import handle_command, validate_storage_name


def main():
    try:
        args, parser = parse_args()
        validate_storage_name(args.storage)
        storage = KVStorage(args.storage, args.dir)
        handle_command(args, storage)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
