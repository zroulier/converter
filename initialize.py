from modules import *
from constants import *
from delete import delete
import sys

terminal_size = os.get_terminal_size()
t_width = terminal_size.columns
t_height = terminal_size.lines
t_width_2 = int(t_width // 2)
t_height_2 = int(t_height // 2)

welcome_msg = 'Welcome to this word finding script!'
welcome_msg_len = int(len(welcome_msg))
new_line = '\n'

def initialize():
    print(Style.RESET_ALL)
    print(new_line * ((t_height_2) + 1))
    
    for i in range(5):
        os.system('cls')
        
        print(new_line * (i * 6))

        print(Fore.YELLOW + '-' * t_width)
        print((' ' * (t_width_2 - (welcome_msg_len // 2))) + welcome_msg + (' ' * (t_width_2 - (welcome_msg_len // 2))))
        print('-' * t_width + Style.RESET_ALL)
        print(Fore.RED + (' ' * (t_width_2 + 4 - welcome_msg_len // 2)) + 'No previous progress found\n')
        print(Fore.GREEN + (' ' * (t_width_2 - 1 - welcome_msg_len // 2)) + 'Intializing script for first time use' + Style.RESET_ALL)
        time.sleep(1)
    time.sleep(3)

    print(new_line * (t_height))
    print(f'{Fore.GREEN}Creating Files...')
    time.sleep(1)
    
    # Create output JSON file
    default_data = []
    if not os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'w') as file:
                json.dump(default_data, file, indent=4)
                print(Fore.GREEN + '\nCreated' + Style.RESET_ALL + ' ' + Fore.BLUE + JSON_FILE + Style.RESET_ALL)
                time.sleep(0.2)
                print(new_line)
                time.sleep(0.2)
        except OSError as e:
            print('Error creating ' + JSON_FILE)
    else:
        print(f'\n{Fore.BLUE} {JSON_FILE} {Fore.YELLOW} already exists{Style.RESET_ALL}')
        print(f'\n{Fore.CYAN}During initialization, files should not be found. A clean installation is recommended to ensure functionality')
        continue_or_not = input('Would you like to close the program? (Y/N)\n' + Style.RESET_ALL)
    
        if continue_or_not.upper() == 'Y':
            sys.exit()
        else:
            print(f'\nContinuing installation with saved version of {Fore.YELLOW}{JSON_FILE}{Style.RESET_ALL}')
            time.sleep(1)

    for log_file in [BATCH_LOG, SESSION_LOG]:
        if not os.path.exists(log_file):
            try:
                with open(log_file, 'w') as file:
                    file.write('')
                print(Fore.GREEN + 'Created' + Style.RESET_ALL + ' ' + Fore.BLUE + log_file + Style.RESET_ALL)
                time.sleep(0.2)
                print(new_line)
                time.sleep(0.2)
            except OSError as e:
                print(f'Error creating log file {log_file}: {e}')
        else:
            print(f'\n{Fore.BLUE} {log_file} {Fore.YELLOW} already exists{Style.RESET_ALL}')
            print(f'\n{Fore.CYAN}During initialization, files should not be found. A clean installation is recommended to ensure functionality')
            continue_or_not = input('Would you like to close the program? (Y/N)\n' + Style.RESET_ALL)

            if continue_or_not.upper() == 'Y':
                sys.exit()
            else:
                print(f'\nContinuing installation with saved version of {Fore.YELLOW}{log_file}{Style.RESET_ALL}')
                time.sleep(1)
    
    if not os.path.exists(UNRECOGNIZED_WORDS_FILE):
        try:
            with open(UNRECOGNIZED_WORDS_FILE, 'w') as file:
                json.dump('', file, indent=4)
                print(Fore.GREEN + 'Created' + Style.RESET_ALL + ' ' + Fore.BLUE + UNRECOGNIZED_WORDS_FILE + Style.RESET_ALL)
                time.sleep(0.2)
                print(new_line)
                time.sleep(1)

        except OSError as e:
            print(Fore.RED + 'Error creating' + Style.RESET + ' ' + UNRECOGNIZED_WORDS_FILE)
    else:
        print(f'\n{Fore.BLUE} {UNRECOGNIZED_WORDS_FILE} {Fore.YELLOW} already exists{Style.RESET_ALL}')
        print(f'\n{Fore.CYAN}During initialization, files should not be found. A clean installation is recommended to ensure functionality')
        continue_or_not = input('Would you like to close the program? (Y/N)\n' + Style.RESET_ALL)

        if continue_or_not.upper() == 'Y':
            sys.exit()
        else:
            print(f'\nContinuing installation with saved version of {Fore.YELLOW}{UNRECOGNIZED_WORDS_FILE}{Style.RESET_ALL}')
            time.sleep(1)
    
    print(new_line * t_height)
    print(Fore.GREEN + 'Installation Success!' + Style.RESET_ALL)
    print(new_line * t_height + Fore.YELLOW + 'Running Session Start...' + Style.RESET_ALL)
    time.sleep(2)

if __name__ == '__main__':
    initialize()