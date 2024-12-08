from transformers import pipeline
from config import Config
import torch
import gc

def load_models():
    try:
        question_generator = pipeline('text2text-generation', model='t5-small', device='cpu')
        intent_classifier = pipeline('text-classification', model='distilbert-base-uncased', device='cpu')
        return question_generator, intent_classifier
    except Exception as e:
        raise RuntimeError(f"Failed to load models: {str(e)}")

question_generator, intent_classifier = load_models()

def generate_questions_and_intents(sentences, batch_size=3):
    qa_pairs = []
    
    # Process in batches
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        
        try:
            with torch.no_grad():
                questions = question_generator(batch, max_length=Config.MAX_QUESTION_LENGTH)
                intents = intent_classifier(batch)
                
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