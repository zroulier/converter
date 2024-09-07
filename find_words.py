import requests
import json
import time
import os
import signal

# Your DictionaryAPI key
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

# Accepted parts of speech
ACCEPTED_POS = {'noun', 'plural noun', 'proverbial saying', 'pronoun', 'verb', 'adjective', 'adverb', 'preposition', 'idiom', 'geographical name'}

# Initialize counters for statistics
total_searches = 0
total_words_recognized = 0
total_words_saved = 0
total_duplicates = 0
total_search_time = 0.0  # To track the total time spent on searches
start_time = time.time()  # Track the start time of the current run
total_elapsed_time = 0.0  # To track the cumulative elapsed time across runs
total_words_processed = 0  # Track the total number of words processed

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
    print("Loading words from file...")
    with open(word_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    print(f"Loaded {len(words)} words.")
    return words

# Load progress (last processed word)
def load_progress():
    print("Loading progress...")
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            last_word = f.read().strip()
            if last_word:
                print(f"Last processed word: {last_word}")
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

# Save total words processed to a file
def save_processed_counter():
    global total_words_processed
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(total_words_processed))

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
                            print(f"Word added: {word} - Part of Speech: {part_of_speech}")
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
                print("JSON decode error. Returning empty list.")
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

# Handle script cancellation and print summary
def signal_handler(signal, frame):
    global start_time, total_words_processed, total_elapsed_time
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("##### SESSION SUMMARY #####")
    print("\n")
    print(f"Total searches: {total_searches}")
    print(f"Total words recognized (API Call Usage): {total_words_recognized}")
    print(f"Total words saved: {total_words_saved}")
    print(f"Total duplicates found: {total_duplicates}")
    
    # Calculate and print the average search time
    if total_searches > 0:
        average_search_time = total_search_time / total_searches
        print(f"Average search time: {average_search_time:.4f} seconds")
    
    # Calculate and print the total time elapsed
    current_run_time = time.time() - start_time
    total_elapsed_time += current_run_time  # Add the current run's time to the total elapsed time
    print(f"Total time elapsed: {total_elapsed_time:.2f} seconds")
    
    # Save total words processed and elapsed time
    save_processed_counter()
    save_elapsed_time()

    # Calculate and print the progress
    progress_percentage = (total_words_processed / TOTAL_WORDS) * 100
    print(f"Progress: {total_words_processed}/{TOTAL_WORDS} ({progress_percentage:.4f}%)")
    
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

    print(f'SAVED BATCH {i // batch_size + 1}. PROGRESS: {total_words_processed}/{TOTAL_WORDS} ({progress_percentage:.4f}%)')
    print(f'ESTIMATED TIME REMAINING: {int(days)}D {int(hours)}H {int(minutes)}M {int(seconds)}S')

# Batch process words, starting from where it left off
def process_words(words, json_file, batch_size=100):
    global total_words_recognized, total_duplicates, total_words_processed  # Declare global variables

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

                # Check if the part of speech is in the accepted list
                if word_info['part_of_speech'] in ACCEPTED_POS:
                    save_to_json(word_info, json_file)  # Save if it matches accepted parts of speech
            else:
                pass

            # Save progress after each word is processed (even if not saved)
            save_progress(word)

            # Adjust the sleep time based on API rate limits
            time.sleep(0.01)  # Adjust based on API rate limit

        # After each batch, calculate and print the progress with remaining time
        print_progress(i, total_words_processed, batch_size)
        
        # Pause after each batch to avoid overwhelming the API
        time.sleep(3)

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
