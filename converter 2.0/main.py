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

TIMEZONE = pytz.timezone('America/New_York')
TOTAL_WORDS = 466433
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'
ACCEPTED_POS = { # Accepted Parts of Speech
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

INPUT_FILE = 'words.txt'
BATCH_LOG = 'batch_log.json'
SESSION_LOG = 'session_log.json'
UNRECOGNIZED_WORDS_FILE = 'unrecognized_words.txt'
CSV_FILE = 'dictionary_words.csv'
JSON_FILE = 'dictionary_words.json'

class UserSession:
    def __init__(self):
        self.is_new_user = self.check_if_new_user()
        self.session_data = self.initialize_session()
        self.start_index = self.get_session_start_index()

    def check_if_new_user(self):
        return not os.path.exists(SESSION_LOG)
        
    def initialize_session(self):
        if self.is_new_user:
            welcome_msg = 'Welcome to this word finding script!'
            welcome_msg_len = int(len(welcome_msg))
            new_line = '\n'
            print(Style.RESET_ALL)
            print(new_line * ((terminal_height // 2) + 1))
            
            for i in range(5):
                os.system('cls')
                print(new_line * (i * 6))
                print(Fore.YELLOW + '-' * terminal_width)
                print((' ' * ((terminal_width // 2) - (welcome_msg_len // 2))) + welcome_msg + (' ' * ((terminal_width // 2) - (welcome_msg_len // 2))))
                print('-' * terminal_width + Style.RESET_ALL)
                print(Fore.RED + (' ' * ((terminal_width // 2) + 4 - welcome_msg_len // 2)) + 'No previous progress found\n')
                print(Fore.GREEN + (' ' * ((terminal_width // 2) - 1 - welcome_msg_len // 2)) + 'Intializing script for first time use' + Style.RESET_ALL)
                time.sleep(1)
            time.sleep(3)

            print(new_line * (terminal_height))
            print(f'{Fore.GREEN}Creating Files...')
            time.sleep(1)
            
            # Create output JSON file
            default_data = []
            if not os.path.exists(CSV_FILE):
                try:
                    with open(CSV_FILE, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Word', 'Part of Speech'])
                        print(Fore.BLUE + '\nCreated ' + Fore.GREEN + CSV_FILE + Style.RESET_ALL)
                        time.sleep(0.2)
                        print(new_line)
                        time.sleep(0.2)
                except OSError as e:
                    print('Error creating ' + CSV_FILE)
            else:
                print(f'\n{Fore.BLUE} {CSV_FILE} {Fore.YELLOW} already exists{Style.RESET_ALL}')
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
            
            print(new_line * terminal_height)
            print(Fore.GREEN + 'Installation Success!' + Style.RESET_ALL)
            print(new_line * terminal_height + Fore.YELLOW + 'Running Session Start...' + Style.RESET_ALL)
            time.sleep(2)

            session_data = {
                'total_search_count': 0,
                'total_sessions': 0,
                'total_saves': 0
            }
            self.save_session_data(session_data)
        else:
            session_data = self.load_session_data()
        return session_data
    
    def save_session_data(self, session_data):
        with open(SESSION_LOG, 'w') as f:
            json.dump(session_data, f)
    
    def load_session_data(self):
        with open(SESSION_LOG, 'r') as f:
            return json.load(f)   

    def get_session_start_index(self):
        with open(CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            return sum(1 for row in reader) - 1

class BatchProcessor:
    def __init__(self, num_batches, lot_size, starting_index):
        self.num_batches = num_batches
        self.lot_size = lot_size
        self.session_batch_count = 0
        self.session_search_count = 0
        self.words_recognized = 0
        self.session_word_count = 0
        self.time_searching = []
        self.index = starting_index
        self.matches = []
        self.recognized = []
        self.unprocessed = []

    def api_request(self, word):
        retries = 3
        for attempt in range(retries):
            try:
                start_search = time.time()
                response = requests.get(API_URL.format(word, API_KEY), timeout=10)
                end_search = time.time()
                self.time_searching.append(end_search - start_search)
                avg_search_time = sum(self.time_searching) / len(self.time_searching)

                if response.status_code == 200:
                    data = response.json()
                    self.session_search_count += 1

                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], dict) and 'fl' in data[0]:
                            part_of_speech = data[0]['fl']
                            self.words_recognized += 1
                            if part_of_speech in ACCEPTED_POS:
                                percentage = ((self.session_search_count / (self.lot_size * self.num_batches)) * 100)
                                print(f'{Fore.RED}[{percentage:.0f}%]{Style.RESET_ALL} FOUND {Fore.CYAN}{word}{Style.RESET_ALL} | Type: {Fore.BLUE}{part_of_speech}{Style.RESET_ALL}')
                                self.session_word_count += 1

                                # Add word and part of speech to csv file here
                                with open(CSV_FILE, mode='a', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow([word, part_of_speech])
                                
                                return {'word': word, 'part_of_speech': part_of_speech}
                    return None
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                print(f'Error processing {word} - retrying ({attempt + 1}/{retries})...')
                time.sleep(2 ** attempt)
        return None
    
    def process_batch(self, words):
        for word in words:
            word_info = self.api_request(word)
            if word_info:
                if word_info['part_of_speech'] in ACCEPTED_POS:
                    self.matches.append(word_info)
                else:
                    self.recognized.append(word_info)
            else:
                self.unprocessed.append(word_info)
    
    def start_batch_loop(self, words):
        for batch_num in range(self.num_batches):

            start_idx = self.index
            end_idx = start_idx + self.lot_size

            batch_words = words[start_idx:end_idx]

            print(f'Starting batch {batch_num + 1}/{self.num_batches}')
            self.process_batch(batch_words)
            self.index += self.lot_size
            print(f'Completed batch {batch_num}/{self.num_batches}')
            print(f'Batch {batch_num + 1} will begin in 5 seconds')
            time.sleep(5)

class LogManager:
    def __init__(self):
        self.session_file = 'session_log.txt'
        self.batch_file = BATCH_LOG

    def log_batch_summary(self, batch_num, system, matches, recognized, unprocessed):
        with open(self.batch_file, "a") as f:
            f.write(f"Batch {batch_num} summary:\n")
            f.write(f'System: {system}')
            f.write(f"Matches: {len(matches)}, Recognized: {len(recognized)}, Unprocessed: {len(unprocessed)}\n")

    def log_session_summary(self, total_batches, system, matches, recognized, unprocessed):
        with open(self.session_file, "a") as f:
            f.write("\nFinal session summary:\n")
            f.write(f'System: {system}')
            f.write(f"Total Batches: {total_batches}\n")
            f.write(f"Matches: {len(matches)}, Recognized: {len(recognized)}, Unprocessed: {len(unprocessed)}\n")

class ProgramManager:
    def __init__(self):
        self.user_session = UserSession()
        self.log_manager = LogManager()

    def run_program(self):

        print(Fore.WHITE + ('\n' * terminal_height) + Fore.YELLOW + 'Begin by entering your session settings below: \n' + Style.RESET_ALL)
        answer = input('Default value of searches per batch is ' + Fore.GREEN + '100' + Style.RESET_ALL + ': ' + Style.RESET_ALL + '\nContinue with default? (Y/N): ')
        if answer.upper() == 'Y':
            lot_size = 100
        if answer.upper() == 'N':
            lot_size = int(input('Enter batch size: '))
        
        print(("#\n" * 5) + Style.BRIGHT + Fore.RED + '**' + Fore.WHITE + str(lot_size) + ' searches per lot' + Fore.RED + '**' + Fore.WHITE)
        num_batches = int(input('Choose Session Lot Size: '))
        system = input(f'Choose your system name for this session: {Style.RESET_ALL}').upper()

        words = self.load_words()

        batch_processor = BatchProcessor(num_batches, lot_size, self.user_session.start_index)
        batch_processor.start_batch_loop(words)

        # Logging after all batch cycles complete
        self.log_manager.log_session_summary(num_batches, system, batch_processor.matches, batch_processor.recognized, batch_processor.unprocessed)
        print("Program finished. Session log saved.")
        self.user_session.session_data['total_sessions'] += 1
        self.user_session.session_data['total_searches'] += num_batches * lot_size
        self.user_session.save_session_data(self.user_session.session_data)

    def load_words(self):
        # Load the words from a file
        with open('words.txt', 'r') as f:
            return [line.strip() for line in f]

if __name__ == '__main__':
    colorama.init()
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines
    program_manager = ProgramManager()
    program_manager.run_program()