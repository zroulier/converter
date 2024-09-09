import os

files = [
    'dictionary_words.json',
    'batch_log.txt',
    'session_log.txt',
    'unrecognized_words.txt'
]

def delete():
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print('Removed ' + file_path)

if __name__ == '__main__':
    delete()