import nltk
import os
from nltk.tokenize import sent_tokenize

# Set multiple data paths
nltk.data.path.extend([
    '/home/dev/nltk_data',
    '/var/www/venv/nltk_data',
    '/usr/share/nltk_data'
])

nltk.download('punkt_tab', quiet=True)

def extract_sentences(text):
    return sent_tokenize(text)

# USAGE
# text = "Your extracted text here..."
# sentences = extract_sentences(text)
# print(sentences)
