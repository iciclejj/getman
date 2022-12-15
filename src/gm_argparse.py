import argparse
import sys

LEGAL_COMMANDS = ['install', 'uninstall', 'update', 'upgrade', 'init']

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
    if command == 'install':
        parser.prog += ' install'
        parser.add_argument('url', help='URL from where to download the deb package')
    elif command == 'uninstall':
        parser.prog += ' uninstall'
        parser.add_argument('package', help='Filename (command) of the package you wish'
                                            ' to upgrade. Source URL can be supplied'
                                            ' instead with -u or --url')
        parser.add_argument('-u', '--url', help='Provide URL instead of filename/command',
                            action='store_true')
    elif command == 'update':
        parser.prog += ' update'
    elif command == 'upgrade':
        parser.prog += ' upgrade'
    elif command =='init':
        parser.prog += ' init'

    args = parser.parse_args(args)

    return command, args, parser

if __name__ == '__main__':
    command, args, parser = init_parser()

    print(f'command:\n{command}\n')
    print(f'args:\n{args}\n')
    print(f'parser:\n{parser}')
