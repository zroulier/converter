from modules import *
from constants import *
import initialize

class FindWords:
    def __init__(self):

        # Initialize terminal dimensions
        self.terminal_size = os.get_terminal_size()
        self.t_width = self.terminal_size.columns
        self.t_height = self.terminal_size.lines
        self.t_width_2 = int(self.t_width // 2)
        self.t_height_2 = int(self.t_height // 2)

        self.batch_size = 100

        # Initialize session counter variables
        self.session_batch_count = 0
        self.session_search_count = 0
        self.words_recognized = 0
        self.session_word_count = 0
        self.time_searching = []
        self.index = 0
        self.session_live_entry_count = 0

    def get_session_count(self):
        try:
            with open(SESSION_LOG, 'r') as f:
                line_count = sum(1 for _ in f)
                session_count = int(line_count / 13)
            return session_count
        except FileNotFoundError:
            print(SESSION_LOG + 'not found')
        return 0

    def log_session(self): # Fix the way this is logged

        if not hasattr(self, 'session_end_time'):
            self.session_end_time = datetime.now(TIMEZONE)

        # self.avg_search_time = (self.session_end_time - self.session_start_time).total_seconds() / self.session_search_count


        if os.path.exists(SESSION_LOG):
            with open(SESSION_LOG, 'r') as f:
                self.log_content = f.readlines()
        else:
            self.log_content = []
        
        session_count = self.get_session_count()

        with open(SESSION_LOG, 'w') as f: # Session log content
            f.write(('-' * 15) + '\n')
            f.write((' ' * 13) + 'Session ' + str(session_count + 1) + ' Summary\n')
            f.write(f'Start time:     {self.session_start_time.strftime("%B")} {self.session_start_time.strftime("%d")}, {self.session_start_time.strftime("%X")}\n')
            f.write(f'End time:       {self.session_end_time.strftime("%B")} {self.session_end_time.strftime("%d")}, {self.session_end_time.strftime("%X")}\n')
            f.write(f'Searches:       {self.session_search_count}\n')
            f.write(f'Average search: {self.avg_search_time} seconds\n')
            f.write(f'API usage:      {self.words_recognized}\n')
            f.write(f'Words saved:    {self.session_word_count}\n')
            f.write(f'Batches:        {self.session_batch_count - 1}\n')
            f.write(f'API Efficiency: {round((self.session_word_count / self.words_recognized) * 100, 2)}%\n')
            f.write(f'Utilization:    {round((self.words_recognized / self.session_search_count) * 100, 2)}%\n')
            f.write('\n' + ('-' * 15) + ('\n' * 3))

            # Append to file
            f.writelines(''.join(self.log_content))

    def start_batches(self, words, start_pos):
        start_pos = self.get_search_index_pos()     
        for i in range(start_pos, TOTAL_WORDS, self.batch_size):
            self.session_batch_count += 1
            self.words_in_batch = 0

            self.batch_start_time = datetime.now(TIMEZONE)

            if self.session_batch_count > self.lot_size:
                self.session_end_time = datetime.now(TIMEZONE)
                # Logic here to stop the session and do anything necessary
                self.save()
                break

            
            batch_words = words[i:i + self.batch_size]
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
        
        try:
            with open(JSON_FILE, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []

        if word_info in existing_data:
            # Add duplicate checker if needed
            print('Duplicate found: ' + (word_info['word']) + ' not saved')
        else:
            existing_data.append(word_info)
            self.session_word_count += 1

            with open(JSON_FILE, 'w') as f:
                json.dump(existing_data, f, indent=4)
                f.write(os.linesep)

    def fetch_entry(self, word):
        self.index += 1
        self.session_live_entry_count +=1
        retries = 3

        for attempt in range(retries):
            try:
                start_search = time.time()
                response = requests.get(API_URL.format(word, API_KEY), timeout=10)
                end_search = time.time()

                self.time_searching.append(end_search - start_search)
                self.avg_search_time = sum(self.time_searching)/len(self.time_searching)

                if response.status_code == 200:
                    data = response.json()
                    self.session_search_count += 1

                    # Filter searches
                    if isinstance(data, list) and len(data) > 0:
                        self.index += 1
                        if isinstance(data[0], dict) and 'fl' in data[0]:
                            part_of_speech = data[0]['fl']

                            # Filter unrecognized POS
                            if part_of_speech in ACCEPTED_POS:
                                if self.session_search_count < 10:
                                    print(f'{Fore.RED}[{(self.session_live_entry_count / (self.lot_size * self.batch_size)) * 100}%]{Style.RESET_ALL}{(' ' * 4)} FOUND {Fore.CYAN}{word}{Style.RESET_ALL}{' ' * (15 - len(word))} | Type: {Fore.BLUE}{part_of_speech}{Style.RESET_ALL}')
                                elif self.session_search_count < 100:
                                    print(f'{Fore.RED}[{int((self.session_live_entry_count / (self.lot_size * self.batch_size)) * 100,0)}%]{Style.RESET_ALL}{('' * 1) + (' ' * 3)} FOUND {Fore.CYAN}{word}{Style.RESET_ALL}{' ' * (15 - len(word))} | Type: {Fore.BLUE}{part_of_speech}{Style.RESET_ALL}')
                                elif self.session_search_count < 1000:
                                    print(f'{Fore.RED}[{int((self.session_live_entry_count / (self.lot_size * self.batch_size)) * 100,0)}%]{Style.RESET_ALL}{('' * 1) + (' ' * 2)} FOUND {Fore.CYAN}{word}{Style.RESET_ALL}{' ' * (15 - len(word))} | Type: {Fore.BLUE}{part_of_speech}{Style.RESET_ALL}')
                                elif self.session_search_count < 10000:
                                    print(f'{Fore.RED}[{int((self.session_live_entry_count / (self.lot_size * self.batch_size)) * 100,0)}%]{Style.RESET_ALL}{('' * 1) + (' ' * 1)} FOUND {Fore.CYAN}{word}{Style.RESET_ALL}{' ' * (15 - len(word))} | Type: {Fore.BLUE}{part_of_speech}{Style.RESET_ALL}')
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
        
        if os.path.exists(BATCH_LOG):
            with open(BATCH_LOG, 'r') as f:
                batch_log_content = f.read()
        else:
            batch_log_content = ''
        
        new_batch_log = log_message + batch_log_content

        with open(BATCH_LOG, 'w') as f:
            f.write(new_batch_log)

    def store_unrecognized_searches(self, word):
        with open(UNRECOGNIZED_WORDS_FILE, 'a') as f:
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
        # print(f'Average time:   {self.avg_search_time} seconds\n')
        print(f'API usage:      {self.words_recognized}\n')
        print(f'Words saved:    {self.session_word_count}\n')
        print(f'Batches:        {self.session_batch_count}\n')
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
                                return last_word.lower()
                    except json.JSONDecodeError:
                        print(f'Error reading {JSON_FILE}')
                        return None
            else:
                print(f'{JSON_FILE} empty')
            return None

    def get_total_word_count(self):
        with open(JSON_FILE, 'r') as f:
            total_words_stats = (sum(1 for line in f) - 4) / 4
            if total_words_stats < 1:
                total_words_stats = 0
                return total_words_stats
            else:
                return total_words_stats

    def get_search_index_pos(self):
        
        # Get last processed search value
        last_word = self.get_last_entry()
        if last_word:
            try:
                with open(WORD_FILE, 'r') as f:
                    for index, line in enumerate(f):
                        if line.strip().lower() == last_word:
                            print(f'Found search #{index + 1} ({last_word})')
                            self.total_search_count = 0
                            self.total_search_count += (index + 1)
                            self.index = self.total_search_count
                            return index
            except FileNotFoundError:
                print(f'Error: File {WORD_FILE} not found.')
                return 0
        else:
            return 0

    def load_data(self):

        self.total_word_count = self.get_total_word_count()

        with open(WORD_FILE, 'r') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        self.total_word_count = self.get_search_index_pos()
        
        remaining = TOTAL_WORDS - self.total_word_count
        print(f'{'\n' * self.t_height}')
        print(f'{Fore.CYAN}Loaded {remaining} remaining searches{Style.RESET_ALL}')
        print(f'{Fore.GREEN}Beginning Batch {self.session_batch_count + 1}... {Style.RESET_ALL}')
        time.sleep(3)
        self.session_start_time = datetime.now(TIMEZONE)
        return words

    # def initialize(self):

    #     initalize.initialize()
    #     self.run()


    def save(self):
        # ALL SAVE LOGS GO HERE FOR A MASTER SAVE FUNCTION
        self.log_session()

    def run(self): # If new user, initialize. Otherwise, input session settings, load data, and start batches
                
        if all(os.path.exists(path) for path in file_paths.values()):
            time.sleep(1)
            print(Fore.WHITE + ('\n' * self.t_height) + Fore.YELLOW + 'Begin by entering your session settings below: \n' + Style.RESET_ALL)
            answer = input('Default value of searches per batch is ' + Fore.GREEN + '100' + Style.RESET_ALL + ': ' + Style.RESET_ALL + '\nContinue with default? (Y/N): ')
            if answer == 'Y':
                self.batch_size = self.batch_size
            elif answer == 'N':
                self.batch_size = int(input('Enter batch size: '))
            
            print(("#\n" * 5) + Style.BRIGHT + Fore.RED + '**' + Fore.WHITE + str(self.batch_size) + ' searches per lot' + Fore.RED + '**' + Fore.WHITE)
            self.lot_size = int(input('Choose Session Lot Size: '))
            self.system = input('Choose your system name for this session: ' + Style.RESET_ALL).upper()
        
            start_pos = self.get_search_index_pos()
            return start_pos if start_pos is not None else 0
        else:
            initialize.initialize()
            self.run()

def main(): # Create instance of FindWords and run

    fw = FindWords()
    start_pos = fw.run()
    words = fw.load_data()
    fw.start_batches(words, start_pos)

if __name__ == '__main__': # Run on execution
    main()










