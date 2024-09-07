import csv
import re
from datetime import datetime

# Read txt file
with open('batch_log.txt', 'r') as file:
    TEXT_FILE = file.read()

def initiate_csv():
    # Create headers
    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Session Number', 'Batch Number', 'Words Saved', 'API Efficiency Rate', 'Batch Utilization Rate', 'System'])

def add_data(file_content):

    # Regex Patterns
    session_pattern = r'Session\s+(\d{1,2})'
    words_pattern = r'Words saved this batch:\s+(\d+)'
    efficiency_pattern = r'API\s+efficiency\s+rate:\s+(\d+\.\d+)'
    utilization_pattern = r'Batch\s+utilization\s+rate:\s+(\d+)'
    system_pattern = r'System:\s+([a-zA-Z]+)'

    session_numbers = re.findall(session_pattern, file_content)
    words_numbers = re.findall(words_pattern, file_content)
    efficiency_numbers = re.findall(efficiency_pattern, file_content)
    utilization_numbers = re.findall(utilization_pattern, file_content)
    system_numbers = re.findall(system_pattern, file_content)

    print(f"Session Numbers: {session_numbers}")
    print(f"Words Numbers: {words_numbers}")
    print(f"Efficiency Numbers: {efficiency_numbers}")
    print(f"Utilization Numbers: {utilization_numbers}")
    print(f"System Numbers: {system_numbers}")

    if len(session_numbers) != len(words_numbers):
        raise ValueError("Corrupted file, delete contents and try again")

    batch_numbers = list(range(len(session_numbers), 0, -1))

    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for session_num, batch_num, words_num, efficiency_num, utilization_num, system_num in zip(session_numbers, batch_numbers, words_numbers, efficiency_numbers, utilization_numbers, system_numbers):
            writer.writerow([session_num, batch_num, words_num, efficiency_num, utilization_num, system_num])

def write_csv(text_file_path):
    # Read the text file content
    with open(text_file_path, 'r') as file:
        file_content = file.read()

    initiate_csv()  # Initialize the CSV with headers
    add_data(file_content)  # Add session, batch, and words saved data

def main():
    write_csv('batch_log.txt')

if __name__ == '__main__':
    main()