import argparse
import sys

def create_parser():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
            prog='getman',
            formatter_class=argparse.RawTextHelpFormatter,
            description='Manage .deb packages from direct web downloads')

    # Add a "command" argument to the parser to specify the command
    # This will also serve as the parent parser for the subcommands
    command_parser = parser.add_subparsers(dest='command', help='The command to run')

    # Call the appropriate function for each command to create the subcommand parsers
    install_parser(command_parser)
    uninstall_parser(command_parser)
    update_parser(command_parser)
    upgrade_parser(command_parser)
    list_parser(command_parser)
    init_parser(command_parser)

    # Parse the command-line arguments
    args = parser.parse_args()

    return args

def install_parser(subparsers):
    parser = subparsers.add_parser('install',
                                   help='Install a package from a URL')
    parser.add_argument('url',
                        help='URL from where to download the binary. This will be the database entry for the package.')
    parser.add_argument('-n', '--name', '--as',
                        help='Provide a custom name for the installed program')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force install even if package already exists in database')

def uninstall_parser(subparsers):
    parser = subparsers.add_parser('uninstall',
                                   help='Uninstall a package')
    parser.add_argument('package',
                        help='Filename (command) of the package you wish to upgrade. Source URL can be supplied instead with -u or --url')
    parser.add_argument('-u', '--url', action='store_true',
                        help='Provide URL instead of filename/command')

def update_parser(subparsers):
    parser = subparsers.add_parser('update',
                                   help='Update the package database')

def upgrade_parser(subparsers):
    parser = subparsers.add_parser('upgrade',
                                   help='Upgrade installed packages')

def list_parser(subparsers):
    parser = subparsers.add_parser('list',
                                   help='List installed packages')

def init_parser(subparsers):
    parser = subparsers.add_parser('init',
                                   help='Initialize the getman environment')
    parser.add_argument('-p', '--purge', action='store_true',
                        help='Delete all getman directories before running initialization')

