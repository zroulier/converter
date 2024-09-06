import ahocorasick
print("Successfully imported")
import re

# Load words from words.txt
def load_words(word_file):
    with open(word_file, 'r') as f:
        words = [line.strip().lower() for line in f if line.strip()]
    return words

# Build Aho-Corasick Automaton
def build_automaton(words):
    A = ahocorasick.Automaton()
    for idx, word in enumerate(words):
        A.add_word(word, (idx, word))
    A.make_automaton()
    return A

# Search for words in the text using the automaton
def search_words(text, automaton):
    word_counts = {}
    for end_index, (idx, word) in automaton.iter(text):
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    return word_counts

def main():
    # Paths to your files
    WORD_FILE = 'words.txt'
    TEXT_FILE = 'text.txt'
    
    # Load and prepare words
    words = load_words(WORD_FILE)
    if not words:
        print("No words loaded from words.txt. Please ensure the file is not empty.")
        return
    
    # Build the Aho-Corasick automaton
    automaton = build_automaton(words)
    
    # Load the text
    with open(TEXT_FILE, 'r') as f:
        text = f.read().lower()  # Convert to lowercase for case-insensitive matching
    
    # Optionally, remove non-alphabetical characters if you expect words to be contiguous
    # cleaned_text = re.sub(r'[^a-z]', '', text)
    # However, since words can be embedded anywhere, it's better to keep the text as is
    
    # Search for words
    word_counts = search_words(text, automaton)
    
    # Print the results
    if word_counts:
        for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{word}: {count}")
    else:
        print("No valid words found.")

if __name__ == "__main__":
    main()
