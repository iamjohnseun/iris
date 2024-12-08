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
nltk.download('stopwords', quiet=True)

def extract_sentences(text, batch_size=1000):
    sentences = []
    paragraphs = text.split('\n')
    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i + batch_size]
        batch_text = ' '.join(batch)
        sentences.extend(sent_tokenize(batch_text))
    return sentences

# USAGE
# text = "Your extracted text here..."
# sentences = extract_sentences(text)
# print(sentences)
