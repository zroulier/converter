import requests
import json
import time
import os

# Your DictionaryAPI key
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

# Load words from a file
def load_words(word_file):
    with open(word_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    return words

# Get word information from DictionaryAPI
def get_word_info(word):
    retries = 3  # Retry up to 3 times for network issues
    for attempt in range(retries):
        try:
            response = requests.get(API_URL.format(word, API_KEY), timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'fl' in data[0]:
                    return {
                        'word': word,
                        'part_of_speech': data[0]['fl']  # Extract part of speech
                    }
            break  # If successful, break the retry loop
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            print(f"Timeout/connection error for word '{word}', retrying ({attempt + 1}/{retries})...")
            time.sleep(2)  # Wait before retrying
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
    existing_data = load_existing_data(json_file)

    # Append new word info only if it's not already present (avoid duplicates)
    if word_info not in existing_data:
        existing_data.append(word_info)
        with open(json_file, 'w') as f:
            json.dump(existing_data, f, indent=4)

# Find the last word processed in the list
def get_last_processed_word(json_file):
    existing_data = load_existing_data(json_file)
    if existing_data:
        return existing_data[-1].get('word')  # Return the last word
    return None  # Return None if no data exists

# Batch process words, skipping already processed ones
def process_words(words, json_file, batch_size=100):
    last_processed_word = get_last_processed_word(json_file)
    
    # Find the position of the last processed word in the word list
    if last_processed_word:
        try:
            start_idx = words.index(last_processed_word) + 1
        except ValueError:
            start_idx = 0  # If the word isn't found, start from the beginning
    else:
        start_idx = 0  # If no word was processed, start from the beginning

    total_words = len(words)
    for i in range(start_idx, total_words, batch_size):
        batch_words = words[i:i + batch_size]
        for word in batch_words:
            word_info = get_word_info(word)
            if word_info:
                save_to_json(word_info, json_file)  # Save after processing each word
                print(f"Processed word: {word_info['word']} - Part of Speech: {word_info['part_of_speech']}")
            time.sleep(0.2)  # Delay between requests to avoid rate-limiting
        print(f"Saved batch {i // batch_size + 1}.")
        time.sleep(5)  # Sleep between batches to avoid overwhelming the API

def main():
    WORD_FILE = 'words.txt'  # The 479k words file from GitHub or Kaggle
    JSON_FILE = 'dictionary_words.json'  # Output file

    # Load words
    words = load_words(WORD_FILE)
    
    # Process words in batches of 100, starting from the last processed word
    process_words(words, JSON_FILE, batch_size=100)

if __name__ == "__main__":
    main()



# import string

# # Load the list of words from words.txt
# with open('words.txt', 'r') as words_file:
#     words = [line.strip().lower() for line in words_file.readlines()]

# # Load the text from text.txt
# with open('text.txt', 'r') as text_file:
#     text = text_file.read()
#     print(text)

# # Create a dictionary to store the word counts
# word_counts = {word: 0 for word in words}
# print(word_counts)

# # Split the text into words and count occurrences of each word
# for word in text.split():
#     # Clean the word by removing punctuation and converting it to lowercase
#     cleaned_word = word.lower().strip(string.punctuation)
#     print(cleaned_word)
    
#     if cleaned_word in word_counts:
#         word_counts[cleaned_word] += 1

# # Filter out words that were not found (corrected with .items())
# found_words = {word: count for word, count in word_counts.items() if count > 0}

# # Print the result
# if found_words:
#     for word, count in found_words.items():
#         print(f"{word}: {count}")
# else:
#     print("No words found.")

# # DATA CLEAN

# # # Load the file and extract the third column from each line
# # with open('core-wordnet.txt', 'r') as file:
# #     lines = file.readlines()

# # # Extract the third column, assuming the format is like the example given
# # # Split by whitespace and get the third item in each line
# # third_column = [line.split()[2] if len(line.split()) > 2 else "" for line in lines]
# # words = [word.strip('[]') for word in third_column]

# # with open('words.txt', 'w') as file:
# #     for word in words:
# #         file.write(word + '\n')