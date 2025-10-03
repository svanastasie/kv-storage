import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="KV-Storage CLI")
    parser.add_argument('--storage', '-s', type=str, default='default',
                        help='Storage name (default: default)')
    parser.add_argument('--dir', '-d', type=str, default='disk',
                        help='Storage directory (default: disk)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # add all commands
    add_command(subparsers)
    add_many_command(subparsers)
    get_command(subparsers)
    delete_command(subparsers)
    other_commands(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    return args, parser


def add_command(subparsers) -> None:
    add_parser = subparsers.add_parser('add', help='Store a key-value pair')
    add_parser.add_argument('key', type=str, help='Key to store')
    add_parser.add_argument('value', type=str, help='Value to store')


def add_many_command(subparsers) -> None:
    add_many_parser = subparsers.add_parser('add-many',
                                            help='Store multiple key-value '
                                                 'pairs from file or '
                                                 'interactively')
    group = add_many_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str,
                       help='Path to CSV/TXT file (format: key,value or '
                            'key;value per line)')
    group.add_argument('--interactive', '-i', action='store_true',
                       help='Enter key-value pairs interactively')


def get_command(subparsers) -> None:
    get_parser = subparsers.add_parser('get', help='Returns a value by key')
    get_parser.add_argument('key', type=str, help='Key to extract')


def delete_command(subparsers) -> None:
    delete_parser = subparsers.add_parser('delete',
                                          help='Delete a key-value pair')
    delete_parser.add_argument('key', type=str, help='Key to delete')


def other_commands(subparsers) -> None:
    subparsers.add_parser('keys', help='List all keys')
    subparsers.add_parser('clear', help='Clear all data.txt')
