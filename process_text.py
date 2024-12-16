import nltk
import os
from config import Config
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Set multiple data paths
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

def extract_sentences(text, batch_size=1000):
    sentences = []
    paragraphs = text.split('\n')
    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i + batch_size]
        batch_text = ' '.join(batch)
        extracted = sent_tokenize(batch_text)
        
        # Filter for meaningful sentences
        meaningful_sentences = [
            sent.strip() 
            for sent in extracted 
            if is_meaningful_sentence(sent)
        ]
        
        sentences.extend(meaningful_sentences)
    
    return sentences

# USAGE
text = "Step 1 Create a free account Create an Atchr account with your personal or business details to get started."
sentences = extract_sentences(text)
print(sentences)
