import argparse
import sys

LEGAL_COMMANDS = ['install', 'uninstall', 'update', 'upgrade', 'list', 'init']

def init_parser():
    command = sys.argv[1]
    args = sys.argv[2:]

    # TODO: allow --help without commands
    #       custom descriptions per command
    parser = argparse.ArgumentParser(
            prog = 'getman',
            description = 'Manage .deb packages from direct web downloads')

    if command not in LEGAL_COMMANDS:
        raise ValueError(f'Unrecognized command. Available commands: {LEGAL_COMMANDS}')

    # TODO: package command-specific parser modifications into their own functions
    #       I think should be able to implement the commands into the parser
    if command == 'install':
        parser.prog += ' install'
        parser.add_argument('url',
                            help='URL from where to download the binary.'
                                 ' This will be the database entry for the package.')
        parser.add_argument('-n', '--name', '--as',
                            help='Provide a custom name for the installed program')
        parser.add_argument('-f', '--force', action='store_true',
                            help='Force install even if package already exists in database')
    elif command == 'uninstall':
        parser.prog += ' uninstall'
        parser.add_argument('package',
                            help='Filename (command) of the package you wish'
                                 ' to upgrade. Source URL can be supplied'
                                 ' instead with -u or --url')
        parser.add_argument('-u', '--url', action='store_true',
                            help='Provide URL instead of filename/command')
    elif command == 'update':
        parser.prog += ' update'
    elif command == 'upgrade':
        parser.prog += ' upgrade'
    elif command == 'list':
        parser.prog += ' list'
    elif command == 'init':
        parser.prog += ' init'

    args = parser.parse_args(args)

    return command, args, parser

if __name__ == '__main__':
    command, args, parser = init_parser()

    print(f'command:\n{command}\n')
    print(f'args:\n{args}\n')
    print(f'parser:\n{parser}')
