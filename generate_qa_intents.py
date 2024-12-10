import torch
import gc
import re
from transformers import pipeline
from config import Config
from urllib.parse import urlparse

_paraphrase_model = None

def get_paraphrase_model():
    global _paraphrase_model
    if _paraphrase_model is None:
        _paraphrase_model = pipeline('text2text-generation', model='t5-base', device='cpu')
    return _paraphrase_model

def load_models():
    try:
        # Load the Question Generation model
        question_generator = pipeline(
            'text2text-generation',
            model='mrm8488/t5-base-finetuned-question-generation-ap',
            device='cpu'
        )

        # Load the Summarization model
        summary_generator = pipeline(
            'summarization',
            model='facebook/bart-large-cnn',
            device='cpu'
        )

        # Load the Paraphrasing model
        paraphrase_model = pipeline(
            'text2text-generation',
            model='Vamsi/T5_Paraphrase_Paws',
            device='cpu'
        )

        return question_generator, summary_generator, paraphrase_model
    except Exception as e:
        raise RuntimeError(f"Failed to load models: {str(e)}")


question_generator, summary_generator, paraphrase_model = load_models()

def clean_text(text):
    # Remove extra whitespace and special characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = re.sub(r'[^\w\s.,!?$€£¥%@#&*()\-]', '', text)  # Keep alphanumeric, common punctuation and symbols
    text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove spaces before punctuation
    text = re.sub(r'[\n\r\t]', ' ', text)  # Replace newlines and tabs with space
    text = re.sub(r'([.,!?])\s+', r'\1 ', text)  # Ensure single space after punctuation
    text = text.replace('..', '.').replace(',,', ',')  # Remove duplicate punctuation
    return text.strip()

def generate_intent_name(text, url):
    from rake_nltk import Rake
    # Extract page name from URL
    path = urlparse(url).path.strip('/')
    page_context = path.split('/')[-1] if path else 'content'

    # Initialize RAKE for keyword extraction
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()
    
    # Use the top keyword as the topic
    topic = keywords[0] if keywords else 'general'

    # Create intent name
    intent_name = f"{page_context}.{topic}".lower().replace(' ', '_')
    
    # Limit intent name length
    intent_name = intent_name[: Config.MAX_INTENT_LENGTH]
    
    return intent_name


def generate_utterances(question, num_variations=5):
    model = get_paraphrase_model()
    
    num_variations = max(7, num_variations)
    
    question = clean_text(question)
    if not question.endswith('?'):
        question += '?'
    
    # Define temperature range for diversity
    temperature_range = [0.6, 0.9, 1.0]
    
    utterances = []
    seen_texts = set()
    
    # Generate variations with different temperatures
    for temp in temperature_range:
        prompt = f"paraphrase: {question}"
        variations = model(
            prompt,
            max_length=Config.MAX_UTTERANCE_LENGTH,
            num_return_sequences=num_variations,
            temperature=temp,
            do_sample=True,
            clean_up_tokenization_spaces=True
        )
        
        for var in variations:
            if isinstance(var, dict):
                if 'generated_text' in var:
                    text = clean_text(var['generated_text'])
                else:
                    text = clean_text(''.join(var.values()))
            elif isinstance(var, str):
                text = clean_text(var)
            else:
                continue

            if (text.endswith('?') and 
                len(text.split()) >= 3 and 
                text.isascii() and 
                text.lower() != question.lower() and
                text not in seen_texts):
                    utterances.append(text)
                    seen_texts.add(text)
    
    return utterances[:num_variations]

def summarize_answer(text):
    temperature_range = [0.3, 0.5, 0.9]
    summaries = []

    # Calculate the lengths based on the input text length
    input_length = len(text.split())
    min_length = max(5, int(input_length * 0.3))  # At least 30% of input length, minimum 5 words
    max_length = max(min_length + 5, int(input_length * 0.7))  # At least min_length + 5, maximum 70% of input length

    for temp in temperature_range:
        summary_results = summary_generator(
            text,
            min_length=min_length,
            max_length=max_length,
            num_return_sequences=1,
            temperature=temp,
            do_sample=True,
            clean_up_tokenization_spaces=True
        )
        if summary_results and isinstance(summary_results, list):
            result = summary_results[0]
            if isinstance(result, dict) and 'summary_text' in result:
                summary = clean_text(result['summary_text'])
            elif isinstance(result, dict) and 'generated_text' in result:
                summary = clean_text(result['generated_text'])
            elif isinstance(result, str):
                summary = clean_text(result)
            else:
                continue

            if summary:
                summaries.append(summary)

    return summaries

def generate_questions_and_intents(sentences, url, batch_size=Config.MAX_BATCH_SIZE):
    sentences = [s for s in sentences if len(s.split()) >= Config.MIN_WORDS_PER_ELEMENT]
    sentences = sentences[:Config.MAX_SENTENCES]
    qa_pairs = []

    torch.set_num_threads(Config.TORCH_THREADS)
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]

        for sentence in batch:
            # Summarize the sentence to get concise answers
            summaries = summarize_answer(sentence)
            if not summaries:
                continue 

            for answer in summaries:
                # Generate questions based on the summarized answer
                question_results = question_generator(
                    answer,
                    max_length=Config.MAX_QUESTION_LENGTH,
                    num_return_sequences=5,
                    temperature=0.7,
                    do_sample=True,
                    clean_up_tokenization_spaces=True
                )

                questions = []
                for result in question_results:
                    if isinstance(result, dict):
                        if 'generated_text' in result:
                            question = clean_text(result['generated_text'])
                        elif 'question' in result:
                            question = clean_text(result['question'])
                        else:
                            question = clean_text(''.join(result.values()))
                    elif isinstance(result, str):
                        question = clean_text(result)
                    else:
                        continue # Skip if the result format is unexpected

                if not question.endswith('?'):
                    question += '?'
                questions.append(question)

            # Generate intent name
            intent_name = generate_intent_name(answer, url)

            # Generate utterances for each question
            for question in questions:
                utterances = generate_utterances(question)

                if utterances:
                    qa_pairs.append({
                        "question": question,
                        "answer": [answer],
                        "intent": intent_name,
                        "utterances": utterances
                    })

        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    return qa_pairs

# USAGE
# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)

#DEBUG
if __name__ == "__main__":
    test_sentences = ["Atchr helps businesses maximize customer engagement by providing automated website visitor interaction tools and real-time analytics to improve conversion rates."]
    
    print(f"Input sentence length: {len(test_sentences[0].split())} words")
    
    # Test summarization
    summaries = summarize_answer(test_sentences[0])
    print(f"Generated summaries: {summaries}")
    
    # Generate full QA pairs
    results = generate_questions_and_intents(test_sentences, "https://www.atchr.com/")
    print("Generated QA pairs:")
    print(results)
