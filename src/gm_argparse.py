import argparse
import sys

LEGAL_COMMANDS = ['install', 'update', 'init']

def init_parser():
    command = sys.argv[1]
    args = sys.argv[2:]

    parser = argparse.ArgumentParser(
            prog = 'getman',
            description = 'Manage .deb packages from direct web downloads')

    if command not in LEGAL_COMMANDS:
        raise ValueError(f'Unrecognized command. Available commands: {LEGAL_COMMANDS}')

    if command == 'install':
        parser.add_argument('url', help='URL from where to download the deb package')
    elif command == 'update':
        pass
    elif command =='init':
        pass

    args = parser.parse_args(args)

    return command, args, parser

if __name__ == '__main__':
    command, args, parser = init_parser()
    print(command)
    print(args)
    print(parser)
