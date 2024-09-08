import pytz

TIMEZONE = pytz.timezone('America/New_York')
BATCH_SIZE = 100
TOTAL_WORDS = 466275
API_KEY = 'f5d9fd44-6ab6-4b32-af6a-f6e75d642ad5'
API_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}'

WORD_FILE = 'words.txt'
JSON_FILE = 'dictionary_words.json'
BATCH_FILE = 'batch_log.txt'

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