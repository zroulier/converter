import os
import time
from colorama import Fore, Style

# Get terminal size
terminal_size = os.get_terminal_size()
t_width = terminal_size.columns
t_height = terminal_size.lines
t_width_2 = int(t_width // 2)

welcome_msg = 'Welcome to this word finding script!'
welcome_msg_len = int(len(welcome_msg))
spaces = ' ' * ((t_width - welcome_msg_len) // 2)

def initialize():
    print(Style.RESET_ALL)
    animation(25)
    os.system('cls')  # Clear the screen after animation is done

def animation(number):
    for i in range(number):
        os.system('cls')  # Clear the screen
        print('\n' * (i * 5))  # Add new lines to simulate moving down
        print(Fore.YELLOW + '-' * t_width)
        print(spaces + welcome_msg + spaces)  # Print the welcome message
        print('-' * t_width + Style.RESET_ALL)
        time.sleep(1)  # Wait for 1 second

if __name__ == '__main__':
    initialize()
