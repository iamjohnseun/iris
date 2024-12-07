from transformers import pipeline
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

def generate_questions_and_intents(sentences, batch_size=8):
    qa_pairs = []
    
    # Process in smaller batches
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        
        # Clear memory between batches
        torch.cuda.empty_cache()
        gc.collect()
        
        for sentence in batch:
            try:
                with torch.no_grad():
                    questions = question_generator(sentence, max_length=64)
                    intent = intent_classifier(sentence)[0]['label']
                    
                    if not isinstance(questions, list):
                        questions = [questions]
                        
                    for q in questions:
                        qa_pairs.append({
                            "question": q['generated_text'],
                            "answer": sentence,
                            "intent": f"faq.{intent.lower().replace(' ', '_')}"
                        })
                        
            except Exception as e:
                continue
                
    return qa_pairs

# USAGE
# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)