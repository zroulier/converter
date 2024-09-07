import requests
import json
import time
import os
import signal
from datetime import datetime
import pytz
from create_csv import write_csv


RUN_TIME = int(input('Choose number of batches for this session\n(100 searches per batch)\nBatch size:'))
# of batches until program stops
SYSTEM = input('What system are you on, | PC | or | Laptop |: ')
if len(SYSTEM) == 2:
    SYSTEM = SYSTEM.upper()
else:
    None


timezone = pytz.timezone('America/New_York')

# Your DictionaryAPI key
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

# Accepted parts of speech
ACCEPTED_POS = {'noun', 'plural noun', 'proverbial saying', 'pronoun', 'verb', 'adjective', 'adverb', 'preposition', 'idiom', 'geographical name', 'exclamation', 'conjunction', 'determiner', 'numeral'}

# Initialize counters for statistics
total_session_batches = 0
total_searches = 0
total_words_recognized = 0
total_words_saved = 0
total_duplicates = 0
total_search_time = 0.0  # To track the total time spent on searches
start_time = time.time()  # Track the start time of the current run
session_start_time = datetime.now(timezone)
total_elapsed_time = 0.0  # To track the cumulative elapsed time across runs
total_words_processed = 0  # Track the total number of words processed
total_api_calls = 0
total_session_count = 0

PROGRESS_FILE = 'progress.txt'  # File to store the progress of the last word processed
COUNTER_FILE = 'counter.txt'    # File to store the cumulative count of words processed
ELAPSED_TIME_FILE = 'elapsed_time.txt'  # File to store the cumulative elapsed time
JSON_FILE = 'dictionary_words.json'  # Output file
TOTAL_WORDS = 466275  # Total number of words in words2.txt

# Load cumulative elapsed time from file
def load_elapsed_time():
    global total_elapsed_time
    if os.path.exists(ELAPSED_TIME_FILE):
        with open(ELAPSED_TIME_FILE, 'r') as f:
            try:
                total_elapsed_time = float(f.read().strip())
            except ValueError:
                total_elapsed_time = 0.0
    else:
        total_elapsed_time = 0.0

# Save cumulative elapsed time to file
def save_elapsed_time():
    global total_elapsed_time
    with open(ELAPSED_TIME_FILE, 'w') as f:
        f.write(str(total_elapsed_time))

# Load words from a file
def load_words(word_file):
    global total_session_count, total_words_processed
    load_session_count()
    print(f'Beginning Session {total_session_count}')
    print("Loading words from file...")
    with open(word_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    load_processed_counter()
    remaining = 466275 - total_words_processed
    print(f"Loaded {remaining} words.")
    return words

# Load progress (last processed word)
def load_progress():
    print("Loading progress...")
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            last_word = f.read().strip()
            if last_word:
                print(f"Loaded last search: {last_word}")
                return last_word
    print("No previous progress found.")
    return None

# Save progress (save the last processed word)
def save_progress(word):
    with open(PROGRESS_FILE, 'w') as f:
        f.write(word)

# Load total words processed from a file
def load_processed_counter():
    global total_words_processed
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            try:
                total_words_processed = int(f.read().strip())
            except ValueError:
                total_words_processed = 0
    else:
        total_words_processed = 0
    return total_words_processed

# Save total words processed to a file
def save_processed_counter():
    global total_words_processed
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(total_words_processed))

def load_apiuse():
    global total_api_calls
    if os.path.exists('api_use.txt'):
        with open('api_use.txt', 'r') as f:
            try:
                total_api_calls = int(f.read().strip())
            except ValueError:
                total_api_calls = 0
    else:
        total_api_calls = 0
    return total_api_calls

def save_api_use():
    global total_api_calls
    with open('api_use.txt', 'w') as f:
        f.write(str(total_api_calls))

def load_session_count():
    global total_session_count
    if os.path.exists('session_count.txt'):
        with open('session_count.txt', 'r') as f:
            try:
                total_session_count = int(f.read().strip())
            except ValueError:
                total_session_count = 1
    else:
        total_session_count = 1
    return total_session_count

def save_session_count():
    global total_session_count
    with open('session_count.txt', 'w') as f:
        f.write(str(total_session_count))

def save_unrecognized_word(word):
    with open('unrecognized_searches.txt', 'a') as f:
        f.write(f'{word}\n')

# Check if a word already exists in the JSON file
def word_exists_in_json(word, json_file):
    existing_data = load_existing_data(json_file)
    for entry in existing_data:
        if entry.get("word") == word:
            return True
    return False

# Get word information from DictionaryAPI and measure search time
def get_word_info(word):
    global total_searches, total_search_time
    total_searches += 1  # Increment the search count only for API requests
    
    retries = 3  # Retry up to 3 times for network issues
    
    for attempt in range(retries):
        try:
            start_time = time.time()  # Start timer
            response = requests.get(API_URL.format(word, API_KEY), timeout=10)
            end_time = time.time()  # End timer
            
            search_duration = end_time - start_time  # Calculate the duration of the search
            total_search_time += search_duration  # Add this duration to the total search time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the data is a list and contains valid objects
                if isinstance(data, list) and len(data) > 0:
                    # Ensure the first item is a dictionary (some responses return lists of suggestions)
                    if isinstance(data[0], dict) and 'fl' in data[0]:
                        part_of_speech = data[0]['fl']
                        
                        # Only print if part of speech is in ACCEPTED_POS
                        if part_of_speech in ACCEPTED_POS:
                            print(f"Found: {word} (Label: {part_of_speech}) --> {total_searches}% complete")
                        return {
                            'word': word,
                            'part_of_speech': part_of_speech  # Extract part of speech
                        }
                    else:
                        return None  # Skip if the data is not in expected format
            break  # If successful, break the retry loop
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print(f"Timeout/connection error for word '{word}', retrying ({attempt + 1}/{retries})...")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None  # Return None if all retries fail

# Read the existing JSON data from the file
def load_existing_data(json_file):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            try:
                return json.load(f)  # Load the JSON array
            except json.JSONDecodeError:
                return []  # Return empty if JSON is invalid
    return []

# Save word data to a JSON file (formats as an array)
def save_to_json(word_info, json_file):
    global total_words_saved, total_duplicates
    existing_data = load_existing_data(json_file)

    # Check for duplicates
    if word_info in existing_data:
        total_duplicates += 1  # Increment duplicate counter
        print(f"Duplicate found: {word_info['word']} (Not saved)")
    else:
        existing_data.append(word_info)
        total_words_saved += 1  # Increment saved words count
        with open(json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)


# Function to update log with session summary and total summary
def update_log():
    global total_searches, total_words_recognized, total_words_saved, total_duplicates, total_session_batches, total_elapsed_time, total_session_count
    
    # Read the current content of the log file
    if os.path.exists('log.txt'):
        with open('log.txt', 'r') as f:
            log_content = f.readlines()
    else:
        log_content = []

    # Calculate total summary based on log and current session
    total_searches_all = total_searches
    total_words_recognized_all = total_words_recognized
    total_words_saved_all = total_words_saved
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
        f.write("\n###############################################\n")
        load_session_count()
        f.write(f"             SESSION {total_session_count} SUMMARY\n")
        x = datetime.now(timezone)
        f.write(f'Session start: {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}\n')
        f.write(f'Session end:   {x.strftime("%A")}, {x.strftime("%B")} {x.strftime("%d")} {x.strftime("%X")}\n')
        f.write(f"Session searches: {total_searches}\n")
        if total_searches > 0:
            average_search_time = total_search_time / total_searches
            f.write(f"Average search time: {average_search_time:.4f} seconds\n")
        f.write(f"Session API usage: {total_words_recognized}\n")
        f.write(f"Session words saved: {total_words_saved}\n")
        f.write(f"Session duplicates found: {total_duplicates}\n")
        f.write(f'Session batches: {total_session_batches - 1}\n')
        f.write(f'API efficiency rate: {round((total_words_saved / total_words_recognized) * 100, 2)}%\n')
        f.write(f'Session utilization rate: {round((total_words_recognized / total_searches) * 100, 2)}%\n')
        f.write("###############################################\n\n")

        # # Write the original log content after the total summary
        f.writelines(log_content)

def print_total_summary():
    global total_elapsed_time
    global total_api_calls
    global total_words_processed
    global total_session_count
    load_session_count()
    load_apiuse()
    
    with open('dictionary_words.json', 'r') as f:
        total_word_stats = (sum(1 for line in f) - 2) / 4

    print("###############################################")
    print(f"               END OF SESSION {total_session_count - 2}")
    print("                TOTAL SUMMARY")
    total_api_calls += total_words_recognized
    print(f'Total API usage: {total_api_calls} ({34333 + total_api_calls} total api count)')
    print(f'Total words saved: {round(total_word_stats, 0)}')
        # Calculate and print the total time elapsed
    current_run_time = time.time() - start_time
    total_elapsed_time += current_run_time  # Add the current run's time to the total elapsed time
    print(f"Total time elapsed: {round(total_elapsed_time,2):.2f} seconds")
        # Calculate and print the progress
    progress_percentage = (total_words_processed / TOTAL_WORDS) * 100
    print(f"Progress: {total_words_processed}/{TOTAL_WORDS} ({progress_percentage:.4f}%)")
    print("###############################################")

# Handle script cancellation and print summary
# Update signal_handler function to include update_log call
def signal_handler(signal, frame):
    global start_time, total_words_processed, total_elapsed_time, total_session_count
    print("\n" * 2)
    print("###############################################")
    print(f"             SESSION {total_session_count - 2} SUMMARY")
    x = datetime.now(timezone)
    print(f'Session start:    {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}')
    print(f'Session end:      {x.strftime("%A")}, {x.strftime("%B")} {x.strftime("%d")} {x.strftime("%X")}')
    print(f"Searches:         {total_searches}")
    # Calculate and print the average search time
    if total_searches > 0:
        average_search_time = total_search_time / total_searches
        print(f"Avg. search time: {average_search_time:.4f} seconds")
    print(f"API usage:        {total_words_recognized}")
    print(f"Words saved:      {total_words_saved}")
    print(f"Doubles found:    {total_duplicates}")
    print(f'Batches:          {total_session_batches - 1}')
    print(f'API efficiency:   {round((total_words_saved / total_words_recognized) * 100, 2)}%')
    print(f'Utilization rate: {round((total_words_recognized / total_searches) * 100, 2)}%')
    print("###############################################")
    print("\n")
    print_total_summary()
    print("\n")
    
    # Call update_log to log the session and total summary
    
    
    # Save total words processed and elapsed time
    save_processed_counter()
    save_api_use()
    save_elapsed_time()
    total_session_count += 1
    save_session_count()
    
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

    save_processed_counter()
    save_elapsed_time()
    save_api_use()

    print("\n" * 25)
    print("###############################################")
    print(f'SAVED BATCH {int(total_searches / 100)}. PROGRESS: {total_words_processed}/{TOTAL_WORDS} ({progress_percentage:.4f}%)')
    print(f'SESSIONS REMAINING: {RUN_TIME - int(total_searches / 100)}')
    print(f'ESTIMATED TIME REMAINING: {int(days)}D {int(hours)}H {int(minutes)}M {int(seconds)}S')
    print(f"WORDS SAVED THIS BATCH: {words_saved_in_batch}")
    print(f'EFFICIENCY RATE OF API: {round(words_saved_in_batch/words_recognized_in_batch * 100, 2)}%')
    print(f'BATCH UTILIZATION RATE: {words_recognized_in_batch}%')
    print("###############################################")
    print("*The next batch will begin in 5 seconds")
    print("\n" * 3)

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
    
    batch_endtime = datetime.now(timezone)

    batch_counter = round(total_searches / 100,0)
    load_session_count()


    log_message = (
        "\n" * 1 +
        f'Session {total_session_count} Batch {int(batch_counter)}\n'
        "###############################################\n" + 
        f'Start Time: {batch_start_time.strftime("%X")}\n' +
        f'End Time: {batch_endtime.strftime("%X")}\n' +
        f'System: {SYSTEM}\n' +
        f'Progress: {total_words_processed}/{TOTAL_WORDS} | {progress_percentage:.5f}%\n' +
        f'Estimated Time Remaining: {int(days)} days, {int(hours)}:{int(minutes)}:{int(seconds)}\n' +
        f"Words saved this batch: {words_saved_in_batch}\n" +
        f'API efficiency rate: {round(words_saved_in_batch/words_recognized_in_batch * 100, 2)}% (90% preferred)\n' +
        f'Batch utilization rate: {words_recognized_in_batch}% (35% preferred)\n' +
        '(percentage of batch time when API was in use)\n' +
        "###############################################\n" +
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


# Batch process words, starting from where it left off
def process_words(words, json_file, batch_size):
    global total_words_recognized, total_duplicates, total_words_processed, total_session_batches  # Declare global variables

    # Load the last processed word
    last_processed_word = load_progress()

    # Find the starting index based on the last processed word
    start_idx = 0
    if last_processed_word:
        try:
            start_idx = words.index(last_processed_word) + 1
        except ValueError:
            print("Last processed word not found in the current word list. Starting from the beginning.")
            start_idx = 0  # If the last word isn't found, start from the beginning

    total_words = len(words)
    for i in range(start_idx, total_words, batch_size):
        global start_time, total_words_processed, total_elapsed_time, words_saved_in_batch, words_recognized_in_batch, total_session_count
        total_session_batches += 1  # Increment the session batch count here
        words_saved_in_batch = 0  # Counter for words saved in the current batch
        words_recognized_in_batch = 0

        # Set the start time for the batch (before processing starts)
        batch_start_time = datetime.now(timezone)  # Correctly store the batch start time

        if total_session_batches > RUN_TIME:
            save_api_use()
            save_elapsed_time()
            save_processed_counter()
            update_log()
            total_session_count += 1
            save_session_count()
            print("\n")
            print("\n")
            print("###############################################")
            load_session_count()
            print(f"             SESSION {total_session_count} SUMMARY")
            x = datetime.now(timezone)
            print(f'Session start: {session_start_time.strftime("%A")}, {session_start_time.strftime("%B")} {session_start_time.strftime("%d")} {session_start_time.strftime("%X")}')
            print(f'Session end:   {x.strftime("%A")}, {x.strftime("%B")} {x.strftime("%d")} {x.strftime("%X")}')
            print(f"Session searches: {total_searches}")
            # Calculate and print the average search time
            if total_searches > 0:
                average_search_time = total_search_time / total_searches
                print(f"Average search time: {average_search_time:.4f} seconds")
            print(f"Session API usage: {total_words_recognized}")
            print(f"Session words saved: {total_words_saved}")
            print(f"Session duplicates found: {total_duplicates}")
            print(f'Session batches: {total_session_batches - 1}')
            print(f'API efficiency rate: {round((total_words_saved / total_words_recognized) * 100, 2)}%')
            print(f'Session utilization rate: {round((total_words_recognized / total_searches) * 100, 2)}%')
            print("###############################################")
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
                save_progress(word)
                continue

            # If the word is not found, query the API
            word_info = get_word_info(word)
            if word_info:
                # Only count the word as recognized if we successfully got valid part of speech data
                if word_info['part_of_speech']:
                    total_words_recognized += 1
                    words_recognized_in_batch += 1

                # Check if the part of speech is in the accepted list
                if word_info['part_of_speech'] in ACCEPTED_POS:
                    save_to_json(word_info, json_file)  # Save if it matches accepted parts of speech
                    words_saved_in_batch += 1  # Increment the count of words saved in this batch
                else:
                    save_unrecognized_word(word)
            else:
                save_unrecognized_word(word)

            # Save progress after each word is processed (even if not saved)
            save_progress(word)

            # Adjust the sleep time based on API rate limits
            time.sleep(0.05)  # Adjust based on API rate limit

        # After the batch finishes processing, set the batch end time
        batch_endtime = datetime.now(timezone)  # Set the end time after the batch completes

        # After each batch, calculate and print the progress with remaining time
        print_progress(i, total_words_processed, batch_size)
        log_progress_to_file(i, total_words_processed, batch_size, start_time, total_elapsed_time, TOTAL_WORDS, words_saved_in_batch, words_recognized_in_batch, batch_start_time, batch_endtime)
        
        # Pause after each batch to avoid overwhelming the API
        write_csv(text_file_path='batch_log.txt')
        time.sleep(5)



def main():
    WORD_FILE = 'words.txt'  # The 479k words file from GitHub or Kaggle
    JSON_FILE = 'dictionary_words.json'  # Output file

    if not os.path.exists(WORD_FILE):
        print(f"Error: Word file '{WORD_FILE}' not found!")
        return

    # Load cumulative total words processed and elapsed time
    load_processed_counter()
    load_elapsed_time()

    # Load words
    words = load_words(WORD_FILE)
    
    # Process words in batches of 100, starting from where it left off
    process_words(words, JSON_FILE, batch_size=100)

if __name__ == "__main__":
    # Register signal handler to handle Ctrl+C interruption
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start main function
    main()
