import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog='getman',
        description='Manage bin packages from direct web downloads')

    subparsers = parser.add_subparsers(
            dest='command',
            required=True,
            help='The command to run')

    # Add subparser for for each command
    _add_install(subparsers)
    _add_uninstall(subparsers)
    _add_update(subparsers)
    _add_upgrade(subparsers)
    _add_list(subparsers)
    _add_init(subparsers)

    return parser

def _add_install(subparsers):
    parser = subparsers.add_parser(
            'install',
            help='Install a package from a URL')

    # arguments
    parser.add_argument(
            'url',
            help='URL from where to download the binary. This will be the'
                 ' database entry for the package.')

    parser.add_argument(
            '-n', '--name', '--as', dest='install_filename',
            help='Provide a custom name for the installed program')

    parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='Force install even if package already exists in database')

def _add_uninstall(subparsers):
    parser = subparsers.add_parser(
            'uninstall',
            help='Uninstall a package')

    # arguments
    parser.add_argument(
            'package',
            help='Filename (command) of the package you wish to upgrade.'
                 ' Source URL can be supplied instead with -u or --url.')

    parser.add_argument(
            '-u', '--url',
            action='store_true',
            help='Provide URL instead of filename/command')

def _add_update(subparsers):
    parser = subparsers.add_parser(
            'update',
            help='Update the package database')

def _add_upgrade(subparsers):
    parser = subparsers.add_parser(
            'upgrade',
            help='Upgrade installed packages')

def _add_list(subparsers):
    parser = subparsers.add_parser(
            'list',
            help='List installed packages')

def _add_init(subparsers):
    parser = subparsers.add_parser(
            'init',
            help='Initialize the getman environment')

    parser.add_argument(
            '-p', '--purge',
            action='store_true',
            help='Delete all getman directories before running initialization')

