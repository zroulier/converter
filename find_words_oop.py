from constants import *
import time
from datetime import datetime
import os
import json
import requests

class FindWords:
    def __init__(self):
        
        # Initialize counter variables
        self.session_start_time = datetime.now(TIMEZONE)
        self.session_batch = 0
        self.session_search_count = 0
        self.words_recognized = 0
        self.session_word_count = 0

    def get_session_count(self):
        try:
            with open('session_log.txt', 'r') as f:
                line_count = sum(1 for _ in f)
                session_count = int(line_count / 13)
            return session_count
        except FileNotFoundError:
            print('session_log.txt not found')
        return 0

    def log_session(self): # Fix the way this is logged

        if not hasattr(self, 'session_end_time'):
            self.session_end_time = datetime.now(TIMEZONE)

        self.avg_search_time = (self.session_end_time - self.session_start_time).total_seconds() / self.session_search_count


        if os.path.exists('session_log.txt'):
            with open('session_log.txt', 'r') as f:
                self.log_content = f.readlines()
        else:
            self.log_content = []
        
        session_count = self.get_session_count()

        with open('session_log.txt', 'a') as f:
            f.write(('-' * 15) + '\n')
            f.write((' ' * 13) + 'Session ' + str(session_count + 1) + ' Summary\n')
            f.write(f'Start time:     {self.session_start_time.strftime("%B")} {self.session_start_time.strftime("%d")}, {self.session_start_time.strftime("%X")}\n')
            f.write(f'End time:       {self.session_end_time.strftime("%B")} {self.session_end_time.strftime("%d")}, {self.session_end_time.strftime("%X")}\n')
            f.write(f'Searches:       {self.session_search_count}\n')
            f.write(f'Average time:   {self.avg_search_time} seconds\n')
            f.write(f'API usage:      {self.words_recognized}\n')
            f.write(f'Words saved:    {self.session_word_count}\n')
            f.write(f'Batches:        {self.session_batch}\n')
            f.write(f'API Efficiency: {round((self.session_word_count / self.words_recognized) * 100, 2)}%\n')
            f.write(f'Utilization:    {round((self.words_recognized / self.session_search_count) * 100, 2)}%\n')
            f.write('\n' + ('-' * 15) + ('\n' * 3))

            # Append to file
            f.writelines(''.join(self.log_content))

    def start_batches(self, words):
        start = self.get_search_index_pos()

        start_idx = 0
        if start is not None:
            start_idx = start
        else:
            start_idx = None
            print('No progress found. Starting First Session...')
        
        total_words = len(words)
        for i in range(start_idx, total_words, BATCH_SIZE):
            self.session_batch += 1
            self.words_in_batch = 0

            self.batch_start_time = datetime.now(TIMEZONE)

            if self.session_batch > self.lot_size:
                self.session_end_time = datetime.now(TIMEZONE)
                # Logic here to stop the session and do anything necessary
                self.save()
                break

            
            batch_words = words[i:i + BATCH_SIZE]
            for word in batch_words:
                word_info = self.fetch_entry(word)
                if word_info:
                    if word_info['part_of_speech']:
                        self.words_recognized += 1
                        self.words_in_batch += 1
                    
                    if word_info['part_of_speech'] in ACCEPTED_POS:
                        self.save_entry(word_info)
                        self.words_in_batch += 1
                    else:
                        self.store_unrecognized_searches(word)
                else:
                    self.store_unrecognized_searches(word)
            
                time.sleep(0.05) # Time between searches
            
            self.batch_end_time = datetime.now(TIMEZONE)

            self.print_end_batch_message()
            self.log_batch() #log progress to file in old file

    def save_entry(self, word_info):
        
        def read_existing_data():
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, 'r') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        return []
            return []

        # Add new entry to existing dataset
        existing_data = read_existing_data()

        if word_info in existing_data:
            # Add duplicate checker if needed
            print('Duplicate found: ' + (word_info['word']) + ' not saved')
        else:
            existing_data.append(word_info)
            self.session_word_count += 1
            with open(JSON_FILE, 'a') as f:
                json.dump(existing_data, f, indent=4)

    def fetch_entry(self, word):
        # self.total_word_count += 1 ###

        retries = 3

        for attempt in range(retries):
            try:
                start_search = time.time()
                response = requests.get(API_URL.format(word, API_KEY), timeout=10)
                end_search = time.time()

                search_duration = end_search - start_search
                search_duration += search_duration

                if response.status_code == 200:
                    data = response.json()
                    self.session_search_count += 1

                    # Filter searches
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], dict) and 'fl' in data[0]:
                            part_of_speech = data[0]['fl']

                            # Filter unrecognized POS
                            if part_of_speech in ACCEPTED_POS:
                                print(f'[{self.session_search_count}%]  FOUND {word} {part_of_speech}')
                            return {
                                'word': word,
                                'part_of_speech': part_of_speech
                            }
                        else:
                            return None
        
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                print(f'Error processing {word} - retrying ({attempt + 1}/{retries})...')
                time.sleep(2 ** attempt) # Exponential back-off
        return None

    def log_batch(self):

        # elapsed_time = time.time() - self.batch_start_time
        session_count = (self.get_session_count)
       
        log_message = (
        "\n" * 1 +
        f'Session {session_count} Batch 2\n'
        "-----------------------------------------------\n" + 
        f'Start Time: {self.batch_start_time.strftime("%X")}\n' +
        f'End Time: {self.batch_end_time.strftime("%X")}\n' +
        f'System: {self.system}\n' +
        f'Progress: {self.total_word_count}/{TOTAL_WORDS} | :.5f%\n' +
        # f'Estimated Time Remaining: {int(days)} days, {int(hours)}:{int(minutes)}:{int(seconds)}\n' +
        f"Words saved this batch: {self.words_in_batch}\n" +
        f'API efficiency rate: {round(self.words_in_batch/self.words_recognized * 100, 2)}%\n' +
        f'Batch utilization rate: {self.words_recognized}%\n' +
        "-----------------------------------------------\n" +
        "\n" * 2
        )

        print(log_message)
        
        if os.path.exists('batch_log.txt'):
            with open('batch_log.txt', 'r') as f:
                batch_log_content = f.read()
        else:
            batch_log_content = ''
        
        new_batch_log = log_message + batch_log_content

        with open('batch_log.txt', 'w') as f:
            f.write(new_batch_log)

    def store_unrecognized_searches(self, word):
        with open('unrecognized_searches.txt', 'a') as f:
            f.write(f'{word}\n')

    def print_end_batch_message(self):
        last_word = self.get_last_entry()
        index = self.get_search_index_pos()
        print(index)
        
    def print_end_session_message(self):

        session_number = self.get_session_count()
        session_number = str(session_number)
        
        with open(JSON_FILE, 'r') as f:
            total_words_num = (sum(1 for line in f) - 2) / 4 # Each word takes up 4 lines in the JSON file, plus two main brackets      
        
        print('-' * 45)
        print((' ' * 10) + 'End of Session' + (session_number))
        print((' ' * 10) + 'Total Statistics')
        print('\n' * 5)

        print((' ' * 10) + 'Session ' + (session_number) +  ' Summary')
        print(f'Start time:     {self.session_start_time.strftime("%B")} {self.session_start_time.strftime("%d")}, {self.session_start_time.strftime("%X")}\n')
        print(f'End time:       {self.session_end_time.strftime("%B")} {self.session_end_time.strftime("%d")}, {self.session_end_time.strftime("%X")}\n')
        print(f'Searches:       {self.session_search_count}\n')
        print(f'Average time:   {self.avg_search_time} seconds\n')
        print(f'API usage:      {self.words_recognized}\n')
        print(f'Words saved:    {self.session_word_count}\n')
        print(f'Batches:        {self.session_batch}\n')
        print(f'API Efficiency: {round((self.session_word_count / self.words_recognized) * 100, 2)}%\n')
        print(f'Utilization:    {round((self.words_recognized / self.session_search_count) * 100, 2)}%\n')
        print('\n' + ('-' * 15) + ('\n' * 3))

    def get_last_entry(self):
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, 'r') as f:
                    try:
                        word_list = json.load(f)
                        if word_list:
                            last_entry = word_list[-1]
                            last_word = last_entry.get('word')
                            if last_word:
                                return last_word
                    except json.JSONDecodeError:
                        print(f'Error reading {JSON_FILE}')
                        return None
            else:
                print(f'{JSON_FILE} not found')
            return None

    def get_total_word_count(self):
        with open(JSON_FILE, 'r') as f:
            total_words_stats = (sum(1 for line in f) - 2) / 4
        return total_words_stats

    def get_search_index_pos(self):
        
        # Get last processed search value
        last_word = self.get_last_entry()
        if last_word:
            last_word = last_word.lower()
        else:
            return 0

        try:
            with open(WORD_FILE, 'r') as f:
                for index, line in enumerate(f):
                    if line.strip().lower() == last_word:
                        print(f'Found {last_word} at line {index + 1}')
                        return index + 1
        except FileNotFoundError:
            print(f'Error: File {WORD_FILE} not found.')
            return 0
        
        print(f'{last_word} not found in {WORD_FILE}.')
        return 0

    def load_data(self):
        with open(WORD_FILE, 'r') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        self.total_word_count = self.get_search_index_pos()
        
        remaining = TOTAL_WORDS - self.total_word_count
        print('Loading progress...')
        print(f'Loaded {remaining} words')
        print(f'First five wordes were loaded: {words[:5]}') ###
        return words

    def save(self):
        # ALL SAVE LOGS GO HERE FOR A MASTER SAVE FUNCTION
        self.log_session()

    def run(self):
        
        # Initialize session settings
        print('Running Word Finding Script...\n' + ('#\n' * 2) + 'Begin by entering your session settings below: ')
        self.lot_size = int(input(("#\n" * 22) + '**' + str(BATCH_SIZE) + 'searches per lot\nChoose Session Lot Size: '))
        self.system = input('Choose your system name for this session: ').upper()
        self.total_word_count = self.get_total_word_count()
        words = self.load_data()
        self.start_batches(words)


def main():
    find_words = FindWords()
    find_words.run()
    find_words.save()
    find_words.print_end_session_message()



if __name__ == '__main__':
    main()