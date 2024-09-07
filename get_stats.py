import re
import statistics
from datetime import datetime
import matplotlib.pyplot as plt

# Define the file name
file_name = "batch_log.txt"

# Regular expressions to capture relevant data
time_regex = re.compile(r"Sat Sep\s+\d+\s+(\d{2}:\d{2}:\d{2})")
words_regex = re.compile(r"Words saved this batch: (\d+)")
api_regex = re.compile(r"API efficiency rate: (\d+\.\d+)%")
utilization_regex = re.compile(r"Batch utilization rate: (\d+)%")

# Initialize lists to store the extracted data
times = []
words_saved = []
api_efficiency = []
batch_utilization = []

# Read the file and extract the data
with open(file_name, 'r') as file:
    text_data = file.read()
    
    # Extracting time, words saved, API efficiency, and utilization
    times = time_regex.findall(text_data)
    words_saved = [int(w) for w in words_regex.findall(text_data)]
    api_efficiency = [float(a) for a in api_regex.findall(text_data)]
    batch_utilization = [int(u) for u in utilization_regex.findall(text_data)]

# Convert times to seconds for batch completion time calculation
time_format = "%H:%M:%S"
time_diffs = []
for i in range(1, len(times)):
    t1 = datetime.strptime(times[i-1], time_format)
    t2 = datetime.strptime(times[i], time_format)
    diff = (t1 - t2).total_seconds()  # time difference in seconds
    time_diffs.append(diff)

# Calculate average values
average_completion_time = statistics.mean(time_diffs)
average_words_saved = statistics.mean(words_saved)
average_api_efficiency = statistics.mean(api_efficiency)
average_batch_utilization = statistics.mean(batch_utilization)

# Convert completion time back to a readable format (seconds to HH:MM:SS)
def convert_seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


average_completion_time_hms = convert_seconds_to_hms(average_completion_time)

# Display the results
results = {
    "Average Completion Time": average_completion_time_hms,
    "Average Words Saved per Batch": average_words_saved,
    "Average API Efficiency Rate (%)": average_api_efficiency,
    "Average Batch Utilization Rate (%)": average_batch_utilization
}

# Function to plot graphs with average value text
def plot_graphs(times, time_diffs, words_saved, api_efficiency, batch_utilization, 
                avg_completion, avg_words, avg_api, avg_utilization):
    plt.figure(figsize=(10, 6))

    # Plot Completion Time per Batch
    plt.subplot(2, 2, 1)
    plt.plot(range(1, len(time_diffs)+1), time_diffs, marker='o')
    plt.title("Completion Time per Batch")
    plt.xlabel("Batch Number")
    plt.ylabel("Time (seconds)")
    plt.ylim(top=250)
    plt.text(0.5, -0.2, f'Average: {average_completion_time_hms}', ha='center', va='center', transform=plt.gca().transAxes)

    # Plot Words Saved per Batch
    plt.subplot(2, 2, 2)
    plt.plot(range(1, len(words_saved)+1), words_saved, marker='o')
    plt.title("Words Saved per Batch")
    plt.xlabel("Batch Number")
    plt.ylabel("Words Saved")
    plt.text(0.5, -0.2, f'Average: {avg_words:.2f}', ha='center', va='center', transform=plt.gca().transAxes)

    # Plot API Efficiency Rate
    plt.subplot(2, 2, 3)
    plt.plot(range(1, len(api_efficiency)+1), api_efficiency, marker='o')
    plt.title("API Efficiency Rate per Batch")
    plt.xlabel("Batch Number")
    plt.ylabel("Efficiency Rate (%)")
    plt.text(0.5, -0.2, f'Average: {avg_api:.2f}%', ha='center', va='center', transform=plt.gca().transAxes)

    # Plot Batch Utilization Rate
    plt.subplot(2, 2, 4)
    plt.plot(range(1, len(batch_utilization)+1), batch_utilization, marker='o')
    plt.title("Batch Utilization Rate per Batch")
    plt.xlabel("Batch Number")
    plt.ylabel("Utilization Rate (%)")
    plt.text(0.5, -0.2, f'Average: {avg_utilization:.2f}%', ha='center', va='center', transform=plt.gca().transAxes)

    plt.tight_layout()
    plt.show()

# Call the function to plot the graphs with average values
plot_graphs(times, time_diffs, words_saved, api_efficiency, batch_utilization,
            average_completion_time_hms, average_words_saved, average_api_efficiency, average_batch_utilization)

# Print the calculated results
for key, value in results.items():
    print(f"{key}: {value}")
