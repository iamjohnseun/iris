from transformers import pipeline
import torch

def load_models():
    try:
        question_generator = pipeline('text2text-generation', model='t5-small')
        intent_classifier = pipeline('text-classification', model='distilbert-base-uncased')
        return question_generator, intent_classifier
    except Exception as e:
        raise RuntimeError(f"Failed to load models: {str(e)}")

question_generator, intent_classifier = load_models()

def generate_questions_and_intents(sentences, batch_size=32):
    qa_pairs = []
    
    # Process in batches to manage memory
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        for sentence in batch:
            try:
                questions = question_generator(sentence)
                if not isinstance(questions, list):
                    questions = [questions]
                intent = intent_classifier(sentence)[0]['label']
                for q in questions:
                    qa_pairs.append({
                        "question": q['generated_text'],
                        "answer": sentence,
                        "intent": f"faq.{intent.lower().replace(' ', '_')}"
                    })
            except torch.cuda.OutOfMemoryError:
                print(f"CUDA out of memory, reducing batch size")
                torch.cuda.empty_cache()
                continue
            except Exception as e:
                print(f"Error processing sentence: {str(e)}")
                continue
                
    return qa_pairs

# USAGE
# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)
