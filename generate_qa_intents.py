from transformers import pipeline
from config import Config
import torch
import gc

def load_models():
    try:
        # Force models to use CPU and smaller batch size
        question_generator = pipeline('text2text-generation', model='t5-small', device='cpu', batch_size=1)
        intent_classifier = pipeline('text-classification', model='distilbert-base-uncased', device='cpu', batch_size=1)
        return question_generator, intent_classifier
    except Exception as e:
        raise RuntimeError(f"Failed to load models: {str(e)}")

question_generator, intent_classifier = load_models()

def generate_questions_and_intents(sentences, batch_size=Config.MAX_BATCH_SIZE):
    sentences = sentences[:Config.MAX_SENTENCES]
    qa_pairs = []
    
    # torch.set_num_threads(Config.TORCH_THREADS)
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    # Process in batches
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        
        try:
            with torch.no_grad():
                questions = question_generator(batch, max_length=Config.MAX_QUESTION_LENGTH, num_return_sequences=1)
                intents = intent_classifier(batch)
                
                if i % (batch_size * 5) == 0:
                    gc.collect()
                
                for q_gen, intent, sentence in zip(questions, intents, batch):
                    qa_pairs.append({
                        "question": q_gen['generated_text'],
                        "answer": sentence,
                        "intent": f"faq.{intent['label'].lower().replace(' ', '_')}"
                    })
                    
        except Exception as e:
            continue
                    
    return qa_pairs

# USAGE
# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)