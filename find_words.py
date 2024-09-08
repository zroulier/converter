import requests
import json
import time
import os
import signal
from datetime import datetime
import pytz
from create_csv import write_csv
from constants import *

# Declare Variables
LOT_SIZE = int(input('Select Lot Size (' + str(BATCH_SIZE) + ' searches per lot)\n: '))
SYSTEM_SESSION = input('What system are you on, | PC | or | Laptop |\n: ').lower()
if SYSTEM_SESSION == 'pc':
    SYSTEM_SESSION = 'PC'
elif SYSTEM_SESSION == 'laptop':
    SYSTEM_SESSION = 'Laptop'
else:
    SYSTEM_SESSION - 'Other'


# Initialize Counters
total_session_batches = 0
total_searches = 0
total_words_recognized = 0
session_words = 0
total_duplicates = 0
total_search_time = 0.0  # To track the total time spent on searches
start_time = time.time()  # Track the start time of the current run
session_start_time = datetime.now(TIMEZONE)
total_elapsed_time = 0.0  # To track the cumulative elapsed time across runs
total_words_processed = 0  # Track the total number of words processed
total_api_calls = 0
total_session_count = 0


# Initial startup
def load_data(word_file):
    session_count = fetch_session_count()
    print(f'Starting Session {session_count + 1}...')
    time.sleep(3)
    print("Loading words from file...")
    with open(word_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    load_progress()
    remaining = 466275 - total_words_processed
    print(f"Loaded {remaining} words.")
    
    print('Loading progress...')
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            try:
                word_list = json.load(f)
                if word_list:
                    last_entry = word_list[-1]
                    last_word = last_entry.get('word')
                    return last_word
            except json.JSONDecodeError:
                print('Error: Could not read the JSON file')
                return None
    else:
        print(f'{JSON_FILE} not found')
    print('No previous progress found')
    print('Beginning First Session...')
    run_batch()

# Load last processed word (progress counter)
def load_progress():
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
                print('Error: Could not read the JSON file')
                return None
    else:
        print(f'{JSON_FILE} not found')
    return None


# Load total words processed from a file
def track_progress(last_word):
    WORD_FILE = 'words.txt'
    try:
        with open(WORD_FILE, 'r') as f:
            for index, line in enumerate(f):
                if line.strip() == last_word:
                    print(f"Found '{last_word}' at line {index + 1}")
                    return index + 1  # Return the line number (1-based index)
    except FileNotFoundError:
        print(f"Error: File '{WORD_FILE}' not found.")
        return None
    
    print(f"'{last_word}' not found in {WORD_FILE}.")
    return None

def fetch_session_count():
    FILE_PATH = 'log.txt'
    try:
        with open(FILE_PATH, 'r') as f:
            line_count = sum(1 for _ in f)
            session_count = line_count / 15
        return session_count
    except FileNotFoundError:
        print(f"Error: File '{FILE_PATH}' not found.")
        return None

def store_unrecognized(word):
    with open('unrecognized_searches.txt', 'a') as f:
        f.write(f'{word}\n')

# Duplicate Filter
def word_exists_in_json(word, json_file):
    existing_data = load_existing_dictionary(json_file)
    for entry in existing_data:
        if entry.get("word") == word:
            return True
    return False

# API Call
def fetch_word(word):
    global total_searches, total_search_time
    total_searches += 1
    
    retries = 3
    
    for attempt in range(retries):
        try:
            start_search = time.time()  # Search timer start
            response = requests.get(API_URL.format(word, API_KEY), timeout=10)
            end_search = time.time()  # Search time end
            
            search_duration = end_search - start_search
            search_duration += search_duration
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter searches
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and 'fl' in data[0]:
                        part_of_speech = data[0]['fl']
                        
                        # Filter out unrecognized calls
                        if part_of_speech in ACCEPTED_POS:
                            print(f"[{round(total_searches / LOT_SIZE, 2)}%]   FOUND {word} {'' * (25 - len(word))} ({part_of_speech})")
                        return {
                            'word': word,
                            'part_of_speech': part_of_speech
                        }
                    else:
                        return None
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print(f"Error processing '{word}' - retrying ({attempt + 1}/{retries})...")
            time.sleep(2 ** attempt)
    return None

# Read the existing JSON data from the file
def load_existing_dictionary(json_file):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Update dictionary file
def save_to_dictionary(word_info, json_file):
    global session_words, total_duplicates
    existing_data = load_existing_dictionary(json_file)

    # Duplicate check
    if word_info in existing_data:
        total_duplicates += 1
        print(f"Duplicate found: {word_info['word']} (Not saved)")
    else:
        existing_data.append(word_info)
        session_words += 1
        with open(json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)


# Save Session Summary
def log_session():
    global total_searches, total_words_recognized, session_words, total_duplicates, total_session_batches, total_elapsed_time, total_session_count
    
    if os.path.exists('log.txt'):
        with open('log.txt', 'r') as f:
            log_content = f.readlines()
    else:
        log_content = []

    # Calculate total summary based on log and current session
    total_searches_all = total_searches
    total_words_recognized_all = total_words_recognized
    total_words_saved_all = session_words
    total_duplicates_all = total_duplicates
    total_batches_all = total_session_batches - 1

    # Extract the previous total summary if present and update values
    if log_content and log_content[0].startswith("Total Summary:"):
        try:
            # Parse previous totals from log file
            total_searches_all += int(log_content[1].split(': ')[1])
            total_words_recognized_all += int(log_content[2].split(': ')[1])
            total_words_saved_all += int(log_content[3].split(': ')[1])
            total_duplicates_all += int(log_content[4].split(': ')[1])
            total_batches_all += int(log_content[5].split(': ')[1])
        except (IndexError, ValueError):
            pass  # In case there's an issue with the previous log, ignore it

    # Write the updated total summary at the top of the file
    with open('log.txt', 'w') as f:
        f.write('\n' + ('-' * 47) + '\n')
        session_count = fetch_session_count()
        f.write((' ' * 13) + f'Session {session_count} Summary\n')
        session_end = datetime.now(TIMEZONE)
        f.write(f'Session start:       {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}\n')
        f.write(f'Session end:         {session_end.strftime("%A")}, {session_end.strftime("%B")} {session_end.strftime("%d")} {session_end.strftime("%X")}\n')
        f.write(f'Session searches:    {total_searches}\n')
        if total_searches > 0:
            average_search_time = total_search_time / total_searches
            f.write(f"Avg. search time:    {average_search_time:.4f} seconds\n")
        f.write(f"Session API usage:   {total_words_recognized}\n")
        f.write(f"Words saved:         {session_words}\n")
        f.write(f"Duplicates found:    {total_duplicates}\n")
        f.write(f'Batches complete:    {total_session_batches - 1}\n')
        f.write(f'API Efficiency:      {round((session_words / total_words_recognized) * 100, 2)}%\n')
        f.write(f'Program Utilization: {round((total_words_recognized / total_searches) * 100, 2)}%\n')
        f.write("###############################################\n\n")

        # # Write the original log content after the total summary
        f.writelines(log_content)

def print_total_summary():
    global total_elapsed_time
    global total_api_calls
    global total_words_processed
    global total_session_count
    session_count = fetch_session_count()
    # load_apiuse()
    
    with open('dictionary_words.json', 'r') as f:
        total_word_stats = (sum(1 for line in f) - 2) / 4

    print("-----------------------------------------------")
    # print(f"               END OF SESSION {session_count - 2}")
    print("                TOTAL SUMMARY")
    total_api_calls += total_words_recognized
    # print(f'Total API usage: {total_api_calls} ({37641 + total_api_calls} total api count)')
    print(f'Total words saved: {round(total_word_stats, 0)}')
        # Calculate and print the total time elapsed
    current_run_time = time.time() - start_time
    total_elapsed_time += current_run_time  # Add the current run's time to the total elapsed time
    print(f"Total time elapsed: {round(total_elapsed_time,2):.2f} seconds")
        # Calculate and print the progress
    total_progress = (total_words_processed / TOTAL_WORDS) * 100
    print(f"Progress: {total_words_processed}/{TOTAL_WORDS} ({total_progress:.4f}%)")
    print("-----------------------------------------------")

# Handle script cancellation and print summary
# Update signal_handler function to include update_log call
def signal_handler(signal, frame):
    session_count = fetch_session_count()
    global start_time, total_words_processed, total_elapsed_time, total_session_count
    print("\n" * 30)
    print("-----------------------------------------------")
    print(f"             SESSION {session_count - 2} SUMMARY")
    x = datetime.now(TIMEZONE)
    print(f'Session start:    {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}')
    print(f'Session end:      {x.strftime("%A")}, {x.strftime("%B")} {x.strftime("%d")} {x.strftime("%X")}')
    print(f"Searches:         {total_searches}")
    # Calculate and print the average search time
    if total_searches > 0:
        average_search_time = total_search_time / total_searches
        print(f"Avg. search time: {average_search_time:.4f} seconds")
    print(f"API usage:        {total_words_recognized}")
    print(f"Words saved:      {session_words}")
    print(f"Doubles found:    {total_duplicates}")
    print(f'Batches:          {total_session_batches - 1}')
    print(f'API efficiency:   {round((session_words / total_words_recognized) * 100, 2)}%')
    print(f'Utilization rate: {round((total_words_recognized / total_searches) * 100, 2)}%')
    print("-----------------------------------------------")
    print("\n")
    print_total_summary()
    print("\n")
    
    exit(0)

# Calculate and print estimated remaining time
def print_progress(i, total_words_processed, batch_size):
    elapsed_time = time.time() - start_time + total_elapsed_time  # Add current elapsed time to total
    progress_percentage = total_words_processed / TOTAL_WORDS * 100
    searches_processed = total_words_processed
    searches_remaining = TOTAL_WORDS - searches_processed
    average_search_time = elapsed_time / searches_processed if searches_processed > 0 else 0
    remaining_time = searches_remaining * average_search_time

    # Convert remaining_time to days, hours, minutes, and seconds
    days, rem = divmod(remaining_time, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    last_word = load_progress()
    last_word_index = track_progress(last_word)
    print(last_word_index)
    
    print("\n" * 35)
    print("-----------------------------------------------")
    print(f'SAVED BATCH {int(total_searches / 100)}. PROGRESS: {last_word_index}/{TOTAL_WORDS} ({progress_percentage:.4f}%)')
    print(f'SESSIONS REMAINING: {LOT_SIZE - int(total_searches / 100)}')
    print(f'ESTIMATED TIME REMAINING: {int(days)}D {int(hours)}H {int(minutes)}M {int(seconds)}S')
    print(f"WORDS SAVED THIS BATCH: {words_saved_in_batch}")
    print(f'EFFICIENCY RATE OF API: {round(words_saved_in_batch/words_recognized_in_batch * 100, 2)}%')
    print(f'BATCH UTILIZATION RATE: {words_recognized_in_batch}%')
    print("-----------------------------------------------")
    print("*The next batch will begin in 5 seconds")
    print("\n" * 1)

def log_progress_to_file(i, total_words_processed, batch_size, start_time, total_elapsed_time, TOTAL_WORDS, words_saved_in_batch, words_recognized_in_batch, batch_start_time, batch_endtime):
    global total_session_count
    elapsed_time = time.time() - start_time + total_elapsed_time  # Add current elapsed time to total
    progress_percentage = total_words_processed / TOTAL_WORDS * 100
    searches_processed = total_words_processed
    searches_remaining = TOTAL_WORDS - searches_processed
    average_search_time = elapsed_time / searches_processed if searches_processed > 0 else 0
    remaining_time = searches_remaining * average_search_time

    # Convert remaining_time to days, hours, minutes, and seconds
    days, rem = divmod(remaining_time, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    
    batch_endtime = datetime.now(TIMEZONE)

    batch_counter = round(total_searches / 100,0)
    session_count = fetch_session_count()


    log_message = (
        "\n" * 1 +
        f'Session {session_count} Batch {int(batch_counter)}\n'
        "-----------------------------------------------\n" + 
        f'Start Time: {batch_start_time.strftime("%X")}\n' +
        f'End Time: {batch_endtime.strftime("%X")}\n' +
        f'System: {SYSTEM_SESSION}\n' +
        f'Progress: {total_words_processed}/{TOTAL_WORDS} | {progress_percentage:.5f}%\n' +
        f'Estimated Time Remaining: {int(days)} days, {int(hours)}:{int(minutes)}:{int(seconds)}\n' +
        f"Words saved this batch: {words_saved_in_batch}\n" +
        f'API efficiency rate: {round(words_saved_in_batch/words_recognized_in_batch * 100, 2)}%\n' +
        f'Batch utilization rate: {words_recognized_in_batch}%\n' +
        "-----------------------------------------------\n" +
        "\n" * 2
    )

    if os.path.exists('batch_log.txt'):
        with open('batch_log.txt', 'r') as f:
            batch_log_content = f.read()
    else:
        batch_log_content = ''
    
    updated_batch_log_content = log_message + batch_log_content

    with open('batch_log.txt', 'w') as f:
        f.write(updated_batch_log_content)


# Begin batch cycle
def run_batch(words, json_file, batch_size):
    global total_words_recognized, total_duplicates, total_words_processed, total_session_batches  # Declare global variables

    # Load the last processed word
    last_search = load_progress()

    # Find where last session left off
    start_idx = 0
    if last_search:
        try:
            start_idx = words.index(last_search) + 1
        except ValueError:
            print("Last processed word not found in the current word list. Starting from the beginning.")
            start_idx = 0  # First time user starts from the beginning

    total_words = len(words)
    for i in range(start_idx, total_words, batch_size):
        global start_time, total_words_processed, total_elapsed_time, words_saved_in_batch, words_recognized_in_batch, total_session_count
        total_session_batches += 1
        words_saved_in_batch = 0
        words_recognized_in_batch = 0

        batch_start_time = datetime.now(TIMEZONE)  # Set batch start time

        if total_session_batches > LOT_SIZE:
            log_session()
            session_count = fetch_session_count()
            print("\n")
            print("\n")
            print("-----------------------------------------------")
            fetch_session_count()
            print(f"             SESSION {session_count} SUMMARY")
            x = datetime.now(TIMEZONE)
            print(f'Session start: {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}')
            print(f'Session end:   {x.strftime("%A")}, {x.strftime("%B")} {x.strftime("%d")} {x.strftime("%X")}')
            print(f"Session searches: {total_searches}")
            # Calculate and print the average search time
            if total_searches > 0:
                average_search_time = total_search_time / total_searches
                print(f"Average search time: {average_search_time:.4f} seconds")
            print(f"Session API usage: {total_words_recognized}")
            print(f"Session words saved: {session_words}")
            print(f"Session duplicates found: {total_duplicates}")
            print(f'Session batches: {total_session_batches - 1}')
            print(f'API efficiency rate: {round((session_words / total_words_recognized) * 100, 2)}%')
            print(f'Session utilization rate: {round((total_words_recognized / total_searches) * 100, 2)}%')
            print("-----------------------------------------------")
            print("\n")
            print_total_summary()
            print("\n")
            
            # Call update_log to log the session and total summary
            
            # Save total words processed and elapsed time
            break
        
        batch_words = words[i:i + batch_size]
        for word in batch_words:
            total_words_processed += 1  # Increment the word processing counter

            # Check if the word already exists in the JSON file to avoid unnecessary API calls
            if word_exists_in_json(word, json_file):
                total_duplicates += 1
                continue

            # If the word is not found, query the API
            word_info = fetch_word(word)
            if word_info:
                # Only count the word as recognized if we successfully got valid part of speech data
                if word_info['part_of_speech']:
                    total_words_recognized += 1
                    words_recognized_in_batch += 1

                # Check if the part of speech is in the accepted list
                if word_info['part_of_speech'] in ACCEPTED_POS:
                    save_to_dictionary(word_info, json_file)  # Save if it matches accepted parts of speech
                    words_saved_in_batch += 1  # Increment the count of words saved in this batch
                else:
                    store_unrecognized(word)
            else:
                store_unrecognized(word)

            # Save progress after each word is processed (even if not saved)

            # Adjust the sleep time based on API rate limits
            time.sleep(0.05)  # Adjust based on API rate limit

        # After the batch finishes processing, set the batch end time
        batch_endtime = datetime.now(TIMEZONE)  # Set the end time after the batch completes

        # After each batch, calculate and print the progress with remaining time
        print_progress(i, total_words_processed, batch_size)
        log_progress_to_file(i, total_words_processed, batch_size, start_time, total_elapsed_time, TOTAL_WORDS, words_saved_in_batch, words_recognized_in_batch, batch_start_time, batch_endtime)
        
        # Pause after each batch to avoid overwhelming the API
        write_csv(text_file_path='batch_log.txt')
        time.sleep(5)





def main():
    if not os.path.exists(WORD_FILE):
        print(f"Error: Word file '{WORD_FILE}' not found!")
        return

    # Find starting index
    load_progress()

    # Load words
    words = load_data(WORD_FILE)
    
    run_batch(words, JSON_FILE, batch_size=BATCH_SIZE)



if __name__ == "__main__":

    # Failsafe which doesn't even work right now; delete it or fix it
    signal.signal(signal.SIGINT, signal_handler)
    
    main()
