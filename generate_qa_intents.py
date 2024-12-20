import torch
import gc
import re
import signal
from config import Config
from transformers import pipeline
from urllib.parse import urlparse
from rake_nltk import Rake

_model = None

def timeout_handler(signum, frame):
    raise TimeoutError("Generation task exceeded time limit")

def get_model():
    global _model
    if _model is None:
        torch.cuda.empty_cache()
        gc.collect()
        _model = pipeline(
            'text2text-generation',
            model='google/flan-t5-large',
            device='cpu',
            model_kwargs={'low_cpu_mem_usage': True}
        )
    return _model

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?$€£¥%@#&*()\-]', '', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = re.sub(r'[\n\r\t]', ' ', text)
    text = re.sub(r'([.,!?])\s+', r'\1 ', text)
    text = text.replace('..', '.').replace(',,', ',')
    return text.strip()

def clean_intent_name(text):
    text = re.sub(r'[\d_]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower().strip().replace(' ', '.')
    text = re.sub(r'\.+$', '', text)
    words = text.split('.')
    if len(words) > 3:
        words = words[:3]
    return '.'.join(words)

def generate_intent_name(text, url):
    path = urlparse(url).path.strip('/')
    page_context = path.split('/')[-1] if path else 'general'
    
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()
    topic = keywords[0] if keywords else 'general'
    
    intent_name = f"{page_context}.{topic}".lower().replace(' ', '_')
    intent_name = clean_intent_name(intent_name)
    return intent_name[:Config.MAX_INTENT_LENGTH]

def generate_utterances(text, num_variations=5):
    model = get_model()
    text = clean_text(text)
    
    temperatures = [0.6, 0.8, 0.9]
    utterances = set()
    
    for temp in temperatures:
        prompt = f"Generate {num_variations} different frequently asked questions (FAQ's) from: {text}"
        variations = model(
            prompt,
            max_length=Config.MAX_UTTERANCE_LENGTH,
            num_return_sequences=num_variations,
            temperature=temp,
            do_sample=True,
            clean_up_tokenization_spaces=True
        )
        
        for var in variations:
            cleaned = clean_text(var['generated_text'])
            if not cleaned.endswith('?'):
                cleaned += '?'
            if len(cleaned.split()) >= 3 and cleaned.isascii():
                utterances.add(cleaned)
    
    return list(utterances)[:num_variations]

def generate_questions_and_intents(sentences, url, is_sync=False, batch_size=Config.MAX_BATCH_SIZE):
    timeout = Config.SYNC_REQUEST_TIMEOUT if is_sync else Config.ASYNC_REQUEST_TIMEOUT
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        sentences = [s for s in sentences if len(s.split()) >= Config.MIN_WORDS_PER_ELEMENT]
        sentences = sentences[:Config.MAX_SENTENCES]
        qa_pairs = []

        torch.set_num_threads(Config.TORCH_THREADS)
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            
            for text in batch:
                text = clean_text(text)
                intent_name = generate_intent_name(text, url)
                utterances = generate_utterances(text)
                
                if utterances:
                    qa_pairs.append({
                        "intent": intent_name,
                        "utterances": utterances,
                        "answer": [text]
                    })

            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

        return qa_pairs
    except TimeoutError:
        return {
            "status": "error",
            "message": "Generation task exceeded time limit",
            "error_type": "timeout"
        }
    finally:
        signal.alarm(0) 
        
# USAGE
# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)