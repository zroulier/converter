import pytz
import os
import requests
import json
import colorama as colorama
from colorama import Fore, Style
import time
from datetime import datetime
import sys
import csv
import shutil

INPUT_FILE = 'words.txt'
OUTPUT_FILE = 'data.csv'
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

ACCEPTED_POS = {
    'noun',
    'plural noun',
    'proverbial saying',
    'pronoun',
    'verb',
    'adjective',
    'adverb',
    'preposition',
    'idiom',
    'geographical name',
    'exclamation',
    'conjunction',
    'determiner',
    'numeral'}

class FindWords:
    def __init__(self):
        self.starting_search_index = 0
        self.session_number = 1
        self.batch_number = 1
        self.total_words_saved = 0
        self.average_search_time = 0
        self.batch_count = 0
        self.total_searches = 0
        self.terminal_size = os.get_terminal_size()
        self.terminal_width =  self.terminal_size.columns
        self.terminal_height = self.terminal_size.lines
        self.columns = shutil.get_terminal_size().columns
        self.session_word_count = 0
        self.session_search_count = 0

    def load_input_data(self):
        if self.starting_search_index == 0: # If starting for the first time
            with open(INPUT_FILE, 'r') as f:
                words = [line.strip().lower() for line in f if line.strip()]
                return words
        else:                               # Optimized by only loading remaining searches
            with open(INPUT_FILE, 'r') as f:
                words = [line.strip().lower() for line in f if line.strip()]
                remaining_data = words[self.total_searches:]
                return remaining_data

    def load_save_point(self): # Get last session number & last word searched & total search count
        with open(OUTPUT_FILE, mode='r', newline='') as file:
            previous_search_time = 0
            reader = csv.reader(file)
            rows = [row for row in reader if any(row)]

            data_rows = rows[1:-1]
            self.aggregate_row = rows[-1]

            for row in data_rows:
                previous_search_time += float(row[5])

            if self.aggregate_row:
                self.total_searches = int(self.aggregate_row[-1])
                self.starting_search_index = self.total_searches + 1 # Starting point for program (total search count should = starting search index - 1)
                self.session_number = int(data_rows[1][0]) + 1
                self.total_words_saved = len(data_rows)
                self.average_search_time = previous_search_time / self.total_words_saved
                # import pdb; pdb.set_trace()
            else:
                self.total_searches = 0

    def initialize(self):
        if not os.path.exists(OUTPUT_FILE): # New user installation
            welcome_msg = 'Welcome to this word finding script!'
            welcome_msg_len = int(len(welcome_msg))
            new_line = '\n'
            print(new_line * ((self.terminal_height // 2) + 1))
            
            for i in range(5): # Start Screen Animation
                os.system('cls')
                print(new_line * (i * 6))
                print(Fore.YELLOW + '-' * self.terminal_width)
                print((' ' * ((self.terminal_width // 2) - (int(len(welcome_msg)) // 2))) + welcome_msg + (' ' * ((self.terminal_width // 2) - (int(len(welcome_msg)) // 2))))
                print('-' * self.terminal_width + Style.RESET_ALL)
                print(Fore.RED + (' ' * ((self.terminal_width // 2) + 4 - int(len(welcome_msg)) // 2)) + 'No previous progress found\n')
                print(Fore.GREEN + (' ' * ((self.terminal_width // 2) - 1 - int(len(welcome_msg)) // 2)) + 'Intializing script for first time use' + Style.RESET_ALL)
                time.sleep(1)
            time.sleep(3) # Start Screen Animation 5 second pause before disappearing

            print(new_line * (self.terminal_height))
            print(f'{Fore.GREEN}Creating Files...')
            time.sleep(1)
            
            # Create output file
            if not os.path.exists(OUTPUT_FILE):
                try:
                    with open(OUTPUT_FILE, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Session Number', 'Batch Number', 'Search Index', 'Word', 'Part of Speech', 'Search Time', 'System Name', 'Aggregate Search Count'])
                        aggregate_row = ['-','-','-','-','-','-','-',0]
                        writer.writerow(aggregate_row)
                        self.aggregate_row = aggregate_row
                        print(f'{Fore.GREEN}\nCreated {Fore.BLUE}{OUTPUT_FILE}{Style.RESET_ALL}')
                        time.sleep(0.2)
                        print(new_line)
                        time.sleep(1)
                except OSError as e:
                    print('Error creating ' + OUTPUT_FILE)
            else:
                print(f'\n{Fore.BLUE} {OUTPUT_FILE} {Fore.YELLOW} already exists{Style.RESET_ALL}')
                print(f'\n{Fore.CYAN}During initialization, files should not be found. A clean installation is recommended to ensure functionality')
                if input('Would you like to close the program? (Y/N)\n' + Style.RESET_ALL).upper() == 'Y':
                    sys.exit()
                else:
                    print(f'\nContinuing installation with saved version of {Fore.YELLOW}{OUTPUT_FILE}{Style.RESET_ALL}')
                    print(f'This is {Fore.RED}{Style.BRIGHT}NOT{Style.RESET_ALL} recommended. Either verify correct file formatting or delete the file and re-run program')
                    time.sleep(1)

            if os.path.exists(INPUT_FILE):
                try:
                    with open(INPUT_FILE, 'r') as file:
                        input_txt_content = file.read()
                        total_index = sum(1 for row in input_txt_content)
                    print(f'{Fore.GREEN}Loaded {Style.RESET_ALL}{Fore.BLUE}{INPUT_FILE}{Style.RESET_ALL}')
                    time.sleep(0.2)
                    print(new_line)
                    time.sleep(0.2)
                except OSError as e:
                    print(f'Error adding {INPUT_FILE} {input}: {e}')
            else:
                print(f'\n{Fore.BLUE}"{INPUT_FILE}"{Fore.RED}NOT{Fore.WHITE} found. Please ensure you cloned the github repository correctly.{Style.RESET_ALL}')

            print(new_line * self.terminal_height)
            print(f'{Fore.GREEN}Installation Success!{Style.RESET_ALL}')
            print(f'{new_line * self.terminal_height}{Fore.YELLOW}Running Session Start...{Style.RESET_ALL}')
            time.sleep(2)
        else: # Returning user load data
            self.load_save_point()

            welcome_msg = 'Welcome back to word finding script!'
            new_line = '\n'
            print(new_line * ((self.terminal_height // 2) + 1))
            
            for i in range(5): # Start Screen Animation
                os.system('cls')
                print(new_line * (i * 6))
                print(Fore.YELLOW + '-' * self.terminal_width)
                print('Welcome back to word finding script!'.center(self.columns))
                print(f'{' ' * ( (self.terminal_height))}') 
                print('-' * self.terminal_width + Style.RESET_ALL)
                print(f'{Fore.CYAN}{round((self.total_searches / 466275) * 100, 2)}% total progress'.center(self.columns))
                print(f'{Fore.CYAN}{self.total_words_saved} words have been saved{Style.RESET_ALL}'.center(self.columns))
                print(f'{Fore.CYAN}{round(self.average_search_time, 4)}s average time per search'.center(self.columns))
                time.sleep(1)
            time.sleep(3) # Start Screen Animation 5 second pause before disappearing

            print(new_line * (self.terminal_height))
            time.sleep(1)

    def choose_session_settings(self, input_data):
        print(f'{Fore.WHITE}{'\n' * self.terminal_height}{Fore.YELLOW}Begin by entering your session settings below: \n{Style.RESET_ALL}')
        if input(f'Default value of searches per batch is {Fore.GREEN}100{Style.RESET_ALL}:{Style.RESET_ALL}\nContinue with default? (Y/N): ').upper() == 'Y':
            self.lot_size = 100
        else:
            self.lot_size = int(input('Enter Lot Size: '))
        print(f'{"#\n" * 5}{Style.BRIGHT + Fore.RED}**{Fore.WHITE} {str(self.lot_size)} searches per lot {Fore.RED}**{Style.RESET_ALL}')
        self.num_batches = int(input('Choose Session Batch Amount: '))
        self.cooldown_time = float(input('Choose Cooldown Time between Batches: '))
        self.session_name = input(f'Choose your system name for this session: {Style.RESET_ALL}').upper()

        print(f'{'\n' * self.terminal_height}')
        print(f'{Fore.CYAN}Loaded {len(input_data)} remaining searches{Style.RESET_ALL}')
        print(f'{Fore.GREEN}Beginning Batch {self.batch_number}... {Style.RESET_ALL}')
        time.sleep(3)

    def api_call(self, word):
        for attempt in range(3):
            try:
                start_search = time.time()
                response = requests.get(API_URL.format(word, API_KEY))
                end_search = time.time()
                search_time = round(end_search - start_search, 6)

                if response.status_code == 200:
                    data = response.json()
                    self.batch_count += 1
                    self.total_searches += 1
                    self.session_search_count += 1
                                        
                    with open(OUTPUT_FILE, 'r') as f:
                        reader = csv.reader(f)
                        rows = [row for row in reader if any(row)]

                    header_row = rows[0]
                    self.aggregate_row = rows[-1]
                    self.aggregate_row[7] = str(self.total_searches)
                    rows[-1] = self.aggregate_row

                    with open(OUTPUT_FILE, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(header_row)
                        for row in rows[1:]:
                            writer.writerow(row)

                    # print(f'Batch searches: {self.batch_count}\nTotal Searches: {self.total_searches}')


                    if isinstance(data, list) and len(data) > 0:
                          if isinstance(data[0], dict) and 'fl' in data[0]:
                            part_of_speech = data[0]['fl']

                            if part_of_speech in ACCEPTED_POS:
                                
                                self.session_word_count += 1

                                percent_batch_complete = round(int((self.batch_count / self.lot_size) * 100),0)
                                percent_session_complete = round(((self.batch_count + ((self.batch_number - 1) * self.lot_size)) / (self.num_batches * self.lot_size)) * 100,0)
                                percent_session_complete = int(percent_session_complete)
                                percent_total_complete = round((self.total_searches / 466275) * 100,0)
                                percent_total_complete = int(percent_total_complete)
                                
                                print(f'{Fore.LIGHTRED_EX}[{percent_total_complete}%][{percent_session_complete}%][{percent_batch_complete}%] {Style.RESET_ALL}{Fore.GREEN}FOUND {Fore.CYAN}{word}{Style.RESET_ALL} | Type: {Fore.YELLOW}{part_of_speech}')
                                
                                new_row = self.session_number, self.batch_number, self.total_searches, word, part_of_speech, search_time, self.session_name, ''
                                rows.insert(1, new_row)

                                with open(OUTPUT_FILE, 'w', newline='') as f:
                                    writer = csv.writer(f)
                                    writer.writerow(header_row)
                                    for row in rows[1:]:
                                        writer.writerow(row)
                                return
                    return None
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                print(f'Error processing {word} - retrying {attempt + 1}/3')
                time.sleep(2 ** attempt)
        return None

    def run_batch_cycle(self, input_data): # Completes a loop of api calls for one batch
        while self.batch_count < self.lot_size:
            word = input_data[self.batch_count + (100 * (self.batch_number - 1))]
            self.api_call(word)
            time.sleep(0.1)

    def end_session(self):
        # Session Summary
        print('\n' * (self.terminal_height // 2))
        print(f'{Fore.LIGHTMAGENTA_EX}Session {self.session_number} Summary'.center(self.columns))
        print(f'Session Start Time: {self.session_start_time}'.center(self.columns))
        print(f'Session End Time: {self.session_end_time}'.center(self.columns))
        print(f'Session Word Count: {self.session_word_count}'.center(self.columns))
        print(f'Average Search Time: {round(self.average_search_time,4)} seconds'.center(self.columns))
        print(f'Total Progress Gained: {round((self.session_search_count / 466275 ) * 100,3)}%'.center(self.columns))
        print(f'{'\n' * 2} You may now safely exit the program.\n\n')
        time.sleep(10)
        sys.exit()
        
    def run(self):
        self.initialize() # Installs if new user, loads progress if returning user

        self.input_data = self.load_input_data() # Loads remaining searches

        self.choose_session_settings(self.input_data) # 
        
        self.session_start_time = datetime.now()
        
        # Batch loop
        while self.batch_number < self.num_batches + 1:
            self.run_batch_cycle(self.input_data)
            self.batch_number += 1
            print('\n' * 10)
            print(f'Batch {self.batch_number} begins in {str(self.cooldown_time)[0]} seconds...')
            print(f'Session progress: {round((self.batch_number/(self.num_batches + 1)) * 100,5)}%')
            time.sleep(self.cooldown_time)
            self.batch_count = 0


        self.session_end_time = datetime.now()

        self.end_session()


if __name__ == '__main__':
    colorama.init()
    find_words = FindWords()
    find_words.run()