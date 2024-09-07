import json
from collections import defaultdict

# Load the JSON data from the file
with open('dictionary_words.json', 'r') as file:
    data = json.load(file)

# Organize words by part of speech
words_by_pos = defaultdict(list)

for entry in data:
    word = entry['word']
    pos = entry['part_of_speech']
    words_by_pos[pos].append(word)

# Sort words within each part of speech alphabetically
for pos in words_by_pos:
    words_by_pos[pos].sort()

# Prepare the cleaned up structure
cleaned_data = []
for pos, words in words_by_pos.items():
    for word in words:
        cleaned_data.append({
            'word': word,
            'part_of_speech': pos
        })

# Save the cleaned data back to a new JSON file
with open('cleaned_dictionary_words.json', 'w') as cleaned_file:
    json.dump(cleaned_data, cleaned_file, indent=4)

print("The JSON file has been cleaned and saved as 'cleaned_dictionary_words.json'.")












# import json

# def remove_duplicates_from_json(file_path):
#     # Read the JSON file line by line
#     with open(file_path, 'r') as file:
#         lines = file.readlines()

#     # Use a set to keep track of unique lines (each line is a dictionary)
#     unique_lines = []
#     seen = set()

#     for line in lines:
#         # Convert the line to a dictionary for comparison
#         line_dict = json.loads(line.strip())
#         line_tuple = tuple(line_dict.items())  # Use a tuple of items to store in the set (dicts are not hashable)

#         if line_tuple not in seen:
#             seen.add(line_tuple)
#             unique_lines.append(line_dict)

#     # Write back the unique lines in proper JSON array format
#     with open(file_path, 'w') as file:
#         json.dump(unique_lines, file, indent=4)

# # Example usage
# remove_duplicates_from_json('dictionary_words.json')
