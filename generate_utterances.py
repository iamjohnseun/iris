from config import Config
from transformers import pipeline
import torch
import gc

def generate_utterances(question):
    try:
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        # Force CPU usage and smaller batch size
        paraphrase = pipeline(
            'text2text-generation',
            model='tuner007/pegasus_paraphrase',
            device='cpu',
            batch_size=1
        )
        
        paraphrases = paraphrase(
            question,
            num_return_sequences=3,
            max_length=Config.MAX_QUESTION_LENGTH,
            clean_up_tokenization_spaces=True
        )
        
        # Force garbage collection
        gc.collect()
        
        return [p['generated_text'] for p in paraphrases]
        
    except Exception as e:
        return [question]

# USAGE
# question = "Can I get a refund?"
# utterances = generate_utterances(question)
# print(utterances)
