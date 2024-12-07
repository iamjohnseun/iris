import nltk
from nltk.tokenize import sent_tokenize

# Set NLTK data path
nltk.data.path.append('/home/dev/nltk_data')
nltk.download('punkt', quiet=True)

def extract_sentences(text):
    return sent_tokenize(text)


# USAGE
# text = "Your extracted text here..."
# sentences = extract_sentences(text)
# print(sentences)
