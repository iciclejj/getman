def prompt_yes_no(message, default=None, modify=True):
    def _modify_message(_message, default):
        if default is None:
            return _message + ' (y/n): '
        
        if default == True:
            return _message + ' (Y/n): '

        if default == False:
            return _message + ' (y/N): '

    if modify:
        message = _modify_message(message, default)

    answer = input(message)

    if answer.lower() in ['y', 'yes']:
        return True

    if answer.lower() in ['n', 'no']:
        return False

    if answer.lower() in [''] and default is not None:
        return default

    return input_yes_no(message, default=default, modify=False)

# TODO: probably create a clearer name and/or add more functionality
def prompt_exact(message, true_inputs, default=None, modify=True):
    def _modify_message(_message, _true_inputs):
        return _message + f'\nEnter {true_inputs} to continue: '

    if modify:
        message = _modify_message(message, true_inputs)

    answer = input(message)

    if answer in true_inputs:
        return True

    return prompt_exact(message, true_inputs, default=default, modify=False)

if __name__ == '__main__':
    return_val = None

    while True:
        default = None
        return_val = prompt_yes_no(f'Testing return value. {default=}',
                                  default=default)
        print(return_val)

        if input('type "continue" to continue: ') == 'continue':
            break

    while True:
        default = True
        return_val = prompt_yes_no(f'Testing return value. {default=}',
                                  default=default)
        print(return_val)

        if input('type "continue" to continue: ') == 'continue':
            break

    while True:
        default = False
        return_val = prompt_yes_no(f'Testing return value. {default=}',
                                  default=default)
        print(return_val)

        if input('type "continue" to continue: ') == 'continue':
            break

    while True:
        default = None
        true_inputs=['ACCEPT']

        return_val = prompt_exact(f'Testing return value. {default=}'
                                  f' {true_inputs=}',
                                  true_inputs=true_inputs,
                                  default=default)

        print(return_val)

        if input('type "continue" to continue: ') == 'continue':
            break
