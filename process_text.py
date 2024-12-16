import nltk
import re
from config import Config
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

nltk.data.path.extend([
    '/home/dev/nltk_data',
    '/var/www/venv/nltk_data',
    '/usr/share/nltk_data'
])

nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

def is_meaningful_sentence(sentence):
    words = sentence.split()
    if len(words) < Config.MIN_WORDS_PER_ELEMENT:
        return False

    stop_words = set(stopwords.words('english'))
    content_words = [w.lower() for w in words if w.lower() not in stop_words]
    if len(content_words) < 2:
        return False
        
    return True

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?$€£¥%@#&*()\-]', '', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = re.sub(r'[\n\r\t]', ' ', text)
    text = re.sub(r'([.,!?])\s+', r'\1 ', text)
    text = text.replace('..', '.').replace(',,', ',')
    text = text[0].upper() + text[1:] if text else text
    return text.strip()

def extract_sentences(text, batch_size=1000):
    sentences = []
    paragraphs = text.split('\n')
    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i + batch_size]
        batch_text = ' '.join(batch)
        extracted = sent_tokenize(batch_text)
        
        meaningful_sentences = [
            sent.strip() 
            for sent in extracted 
            if is_meaningful_sentence(sent)
        ]
        
        sentences.extend(meaningful_sentences)
    
    return sentences

# USAGE
# text = "A sample token to test the functionality of this script. Let's get started."
# sentences = extract_sentences(text)
# print(sentences)
