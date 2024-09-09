from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# List of colors to cycle through
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

# Function to print a rainbow hash line
def rainbow_hash_line(length):
    rainbow_line = ""
    
    # Loop to create the rainbow hash line
    for i in range(length):
        rainbow_line += colors[i % len(colors)] + "#"
    
    # Print the rainbow line
    print(rainbow_line + Style.RESET_ALL)

# Call the function to create a rainbow hash line of length 50
rainbow_hash_line(50)
