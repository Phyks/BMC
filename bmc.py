#!/usr/bin/env python3

import argparse
import os
import sys

from backend import commands
from backend import tools
from backend.config import Config

# TODO: Handle config


# Load EDITOR variable
EDITOR = os.environ.get("EDITOR")


def file_or_id_from_args(args):
    """
    Helper function to parse provided args to check if the argument is a \
            file or an identifier.
    """
    return "id" if args.id else "file" if args.file else None


def parse_args():
    """
    Build a parser and parse arguments of command line.

    :returns: Parsed arguments from the parser.
    """
    parser = argparse.ArgumentParser(
        description="A bibliography management tool.")
    parser.add_argument("-c", "--config", default=None,
                        help="path to a custom config dir.")
    subparsers = parser.add_subparsers(help="sub-command help", dest='command')
    subparsers.required = True  # Fix for Python 3.3.5

    parser_download = subparsers.add_parser('download', help="download help")
    parser_download.add_argument('-m', '--manual', default=False,
                                 action='store_true',
                                 help="disable auto-download of bibtex")
    parser_download.add_argument('-y', default=False,
                                 help="Confirm all")
    parser_download.add_argument('--tag', default='',
                                 help="Tag")
    parser_download.add_argument('--keep', default=False,
                                 help="Do not remove the file")
    parser_download.add_argument('url',  nargs='+',
                                 help="url of the file to import")
    parser_download.set_defaults(func='download')

    parser_import = subparsers.add_parser('import', help="import help")
    parser_import.add_argument('-m', '--manual', default=False,
                               action='store_true',
                               help="disable auto-download of bibtex")
    parser_import.add_argument('-y', default=False,
                               help="Confirm all")
    parser_import.add_argument('--tag', default='', help="Tag")
    parser_import.add_argument('--in-place', default=False,
                               dest="inplace", action='store_true',
                               help="Leave the imported file in place",)
    parser_import.add_argument('file',  nargs='+',
                               help="path to the file to import")
    parser_import.add_argument('--skip',  nargs='+',
                               help="path to files to skip", default=[])
    parser_import.set_defaults(func='import')

    parser_delete = subparsers.add_parser('delete', help="delete help")
    parser_delete.add_argument('entries', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_delete.add_argument('--skip',  nargs='+',
                               help="path to files to skip", default=[])
    group = parser_delete.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_delete.add_argument('-f', '--force', default=False,
                               action='store_true',
                               help="delete without confirmation")
    parser_delete.set_defaults(func='delete')

    parser_edit = subparsers.add_parser('edit', help="edit help")
    parser_edit.add_argument('entries', metavar='entry', nargs='+',
                             help="a filename or an identifier")
    parser_edit.add_argument('--skip',  nargs='+',
                             help="path to files to skip", default=[])
    group = parser_edit.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_edit.set_defaults(func='edit')

    parser_list = subparsers.add_parser('list', help="list help")
    parser_list.set_defaults(func='list')

    parser_open = subparsers.add_parser('open', help="open help")
    parser_open.add_argument('ids', metavar='id',  nargs='+',
                             help="an identifier")
    parser_open.set_defaults(func='open')

    parser_export = subparsers.add_parser('export', help="export help")
    parser_export.add_argument('entries', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_export.add_argument('--skip',  nargs='+',
                               help="path to files to skip", default=[])
    group = parser_export.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_export.set_defaults(func='export')

    parser_resync = subparsers.add_parser('resync', help="resync help")
    parser_resync.set_defaults(func='resync')

    parser_update = subparsers.add_parser('update', help="update help")
    parser_update.add_argument('entries', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_update.add_argument('--skip',  nargs='+',
                               help="path to files to skip", default=[])
    group = parser_update.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_update.set_defaults(func='update')

    return parser.parse_args()


def main():
    """
    Main function.
    """
    global config

    # Parse arguments
    args = parse_args()

    # Load the custom config if needed
    if args.config is not None:
        config = Config(base_config_path=args.config)

    # Download command
    if args.func == 'download':
        skipped = []
        for url in args.url:
            # Try to download the URL
            new_name = commands.download(url, args.manual, args.y,
                                         args.tag)
            if new_name is not None:
                print("%s successfully imported as %s." % (url, new_name))
            else:
                tools.warning("An error occurred while downloading %s." %
                              (url,))
                skipped.append(url)
        # Output URLs with errors
        if len(skipped) > 0:
            tools.warning("Skipped URLs:")
            for i in skipped:
                tools.warning(i)

    # Import command
    elif args.func == 'import':
        skipped = []
        # Handle exclusions
        files_to_process = list(set(args.file) - set(args.skip))
        for filename in files_to_process:
            # Try to import the file
            new_name = commands.import_file(filename,
                                            args.manual, args.y,
                                            args.tag, not args.inplace)
            if new_name is not None:
                print("%s successfully imported as %s." % (filename, new_name))
            else:
                tools.warning("An error occurred while importing %s." %
                              (filename,))
                skipped.append(filename)
        # Output files with errors
        if len(skipped) > 0:
            tools.warning("Skipped files:")
            for i in skipped:
                tools.warning(i)

    # Delete command
    elif args.func == 'delete':
        skipped = []
        # Handle exclusions
        items_to_process = list(set(args.entries) - set(args.skip))
        for item in items_to_process:
            # Confirm before deletion
            if not args.force:
                confirm = input("Are you sure you want to delete %s? [y/N] " %
                                (item,))
            else:
                confirm = 'y'

            # Try to delete the item
            if confirm.lower() == 'y':
                file_or_id = file_or_id_from_args(args)
                commands.delete(item, args.keep, file_or_id)
                print("%s successfully deleted." % (item,))
            else:
                skipped.append(item)
        # Output items with errors
        if len(skipped) > 0:
            tools.warning("Skipped items:")
            for i in skipped:
                tools.warning(i)

    # Edit command
    elif args.func == 'edit':
        # Handle exclusions
        items_to_process = list(set(args.entries) - set(args.skip))
        for item in items_to_process:
            file_or_id = file_or_id_from_args(args)
            commands.edit(item, file_or_id)

    # List command
    elif args.func == 'list':
        # List all available items
        for id, file in commands.list_entries().items():
            # And print them as "identifier: file"
            print("%s: %s" % (id, file))

    # Open command
    elif args.func == 'open':
        # Open each entry
        for id in args.ids:
            if not commands.open(id):
                # And warn the user about missing files or errors
                tools.warning("Unable to open file associated with ident %s." %
                              (id,))

    # Export command
    elif args.func == 'export':
        # Handle exclusions
        items_to_process = list(set(args.entries) - set(args.skip))
        for item in items_to_process:
            file_or_id = file_or_id_from_args(args)
            print(commands.export(item, file_or_id))

    # Resync command
    elif args.func == 'resync':
        confirm = input("Resync files and bibtex index? [y/N] ")
        if confirm.lower() == 'y':
            commands.resync()

    # Update command
    elif args.func == 'update':
        # Handle exclusions
        items_to_process = list(set(args.entries) - set(args.skip))
        for item in items_to_process:
            file_or_id = file_or_id_from_args(args)
            updates = commands.update(args.entries)
            # TODO \/
            print("%d new versions of papers were found:" % (len(updates)))
            for item in updates:
                print(item)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
