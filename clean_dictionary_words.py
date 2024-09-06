import json

def remove_duplicates_from_json(file_path):
    # Read the JSON file line by line
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Use a set to keep track of unique lines (each line is a dictionary)
    unique_lines = []
    seen = set()

    for line in lines:
        # Convert the line to a dictionary for comparison
        line_dict = json.loads(line.strip())
        line_tuple = tuple(line_dict.items())  # Use a tuple of items to store in the set (dicts are not hashable)

        if line_tuple not in seen:
            seen.add(line_tuple)
            unique_lines.append(line_dict)

    # Write back the unique lines in proper JSON array format
    with open(file_path, 'w') as file:
        json.dump(unique_lines, file, indent=4)

# Example usage
remove_duplicates_from_json('dictionary_words.json')
