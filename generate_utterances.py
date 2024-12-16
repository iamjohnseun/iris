from transformers import pipeline
import torch
import gc

# Global model instance
_paraphrase_model = None

def get_paraphrase_model():
    global _paraphrase_model
    if _paraphrase_model is None:
        _paraphrase_model = pipeline(
            'text2text-generation',
            model='google/flan-t5-large',
            device='cpu',
            batch_size=1
        )
    return _paraphrase_model

def generate_utterances(question):
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        model = get_paraphrase_model()
        paraphrases = model(
            question,
            num_return_sequences=3,
            max_length=50,
            clean_up_tokenization_spaces=True
        )
        
        gc.collect()
        return [p['generated_text'] for p in paraphrases]
        
    except Exception as e:
        return [question]

# USAGE
# question = "Can I get a refund?"
# utterances = generate_utterances(question)
# print(utterances)
