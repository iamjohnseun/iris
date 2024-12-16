import nltk
import re
from config import Config
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from transformers import pipeline

nltk.data.path.extend([
    '/home/dev/nltk_data',
    '/var/www/venv/nltk_data',
    '/usr/share/nltk_data'
])

nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

_paraphrase_model = None

def get_paraphrase_model():
    global _paraphrase_model
    if _paraphrase_model is None:
        _paraphrase_model = pipeline(
            'text2text-generation',
            model='t5-small',
            device='cpu'
        )
    return _paraphrase_model

def paraphrase_sentence(sentence):
    model = get_paraphrase_model()
    prefix = "paraphrase: "
    try:
        result = model(prefix + sentence, 
                      max_length=100,
                      do_sample=True,
                      temperature=0.7,
                      num_beams=2)
        return result[0]['generated_text']
    except:
        return sentence

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
        
        # meaningful_sentences = [
        #     sent.strip() 
        #     for sent in extracted 
        #     if is_meaningful_sentence(sent)
        # ]
        meaningful_sentences = []
        for sent in extracted:
            if is_meaningful_sentence(sent):
                cleaned = clean_text(sent)
                paraphrased = paraphrase_sentence(cleaned)
                meaningful_sentences.append(paraphrased)
        
        sentences.extend(meaningful_sentences)
    
    return sentences

# USAGE
text = """
Step 1: Create a free account. Create an Atchr account with your personal or business details to get started.
Step 2: Upon registration, you'll receive your unique embed code to add to your website.
Step 3: Your widget will be ready for seamless, direct communication with your customers.
"""
sentences = extract_sentences(text)
# print(sentences)
for i, sentence in enumerate(sentences, 1):
    print(f"{i}. {sentence}")
