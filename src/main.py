import command_handlers
from gm_argparse import create_parser
from init_getman import init_getman, needs_init

def main():
    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    if needs_init() and args.command != 'init':
        answer = input('Missing getman files detected. Run initialization?'
                       ' (Will ask before deleting or overwriting files).'
                       ' (y/N): ')

        if answer.lower in ['y', 'yes']:
            init_getman()

    if needs_init() and args.command != 'init':
        print('Missing required files. Exiting. Nothing has been done.')
        return

    command_handler = getattr(command_handlers, args.command + '_')
    command_handler(**vars(args))

if __name__ == '__main__':
    main()

