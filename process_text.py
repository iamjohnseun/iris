import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')

def extract_sentences(text):
    return sent_tokenize(text)

# USAGE

# text = "Your extracted text here..."
# sentences = extract_sentences(text)
# print(sentences)
