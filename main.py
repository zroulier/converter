import json

def convert_txt_to_json(txt_file, json_file):
    # Initialize an empty list to hold the words
    words_list = []

    # Open the text file and read the words
    with open(txt_file, 'r') as file:
        for line in file:
            # Strip any newline characters and add the word to the list
            word = line.strip()
            words_list.append(word)

    # Write the list to a JSON file
    with open(json_file, 'w') as json_out:
        json.dump(words_list, json_out, indent=4)  # Use indent=4 for pretty formatting

# Specify input and output file paths
txt_file = 'words.txt'
json_file = 'words.json'

# Convert the txt file to json
convert_txt_to_json(txt_file, json_file)

print(f"Converted {txt_file} to {json_file} successfully.")
