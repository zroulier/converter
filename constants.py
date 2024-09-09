from modules import *

TIMEZONE = pytz.timezone('America/New_York')
TOTAL_WORDS = 466433
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

file_paths = {
    'JSON_FILE': 'dictionary_words.json',
    'BATCH_LOG': 'batch_log.txt',
    'SESSION_LOG': 'session_log.txt',
    'UNRECOGNIZED_WORDS_FILE': 'unrecognized_words.txt'
}

WORD_FILE = 'words.txt'
JSON_FILE = 'dictionary_words.json'
BATCH_LOG = 'batch_log.txt'
SESSION_LOG = 'session_log.txt'
UNRECOGNIZED_WORDS_FILE = 'unrecognized_words.txt'


ACCEPTED_POS = {
    'noun',
    'plural noun',
    'proverbial saying',
    'pronoun',
    'verb',
    'adjective',
    'adverb',
    'preposition',
    'idiom',
    'geographical name',
    'exclamation',
    'conjunction',
    'determiner',
    'numeral'}