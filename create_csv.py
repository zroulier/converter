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
        writer.writerow(['Session Number', 'Batch Number', 'Words Saved', 'API Efficiency Rate', 'Batch Utilization Rate', 'System', 'Duration (seconds)'])

def add_data(file_content):

    # Regex Patterns
    session_pattern = r'Session\s+(\d{1,2})'
    words_pattern = r'Words saved this batch:\s+(\d+)'
    efficiency_pattern = r'API\s+efficiency\s+rate:\s+(\d+\.\d+)'
    utilization_pattern = r'Batch\s+utilization\s+rate:\s+(\d+)'
    system_pattern = r'System:\s+([a-zA-Z]+)'
    start_time_pattern = r'Start\s+Time:\s+\d+:(\d+):(\d+)'
    end_time_pattern = r'End\s+Time:\s+\d+:(\d+):(\d+)'

    session_numbers = re.findall(session_pattern, file_content)
    words_numbers = re.findall(words_pattern, file_content)
    efficiency_numbers = re.findall(efficiency_pattern, file_content)
    utilization_numbers = re.findall(utilization_pattern, file_content)
    system_numbers = re.findall(system_pattern, file_content)
    start_times = re.findall(start_time_pattern, file_content)
    end_times = re.findall(end_time_pattern, file_content)

    if len(session_numbers) != len(words_numbers):
        raise ValueError("Corrupted file, delete contents and try again")

    batch_numbers = list(range(len(session_numbers), 0, -1))

    time_differences = []

    for start_time, end_time in zip(start_times, end_times):
        start_minutes, start_seconds = int(start_time[0]), int(start_time[1])
        end_minutes, end_seconds = int(end_time[0]), int(end_time[1])

        # Calculate the differences
        minutes_diff = end_minutes - start_minutes
        seconds_diff = end_seconds - start_seconds

        # Handle negative seconds difference by adjusting the minutes difference
        if seconds_diff < 0:
            minutes_diff -= 1
            seconds_diff += 60

        # Append the differences to the list
        time_differences.append((minutes_diff, seconds_diff))

    with open('data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for session_num, batch_num, words_num, efficiency_num, utilization_num, system_num, time_diff in zip(session_numbers, batch_numbers, words_numbers, efficiency_numbers, utilization_numbers, system_numbers, time_differences):
            minutes_diff, seconds_diff = time_diff
            writer.writerow([session_num, batch_num, words_num, efficiency_num, utilization_num, system_num, (minutes_diff*60) + seconds_diff])

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