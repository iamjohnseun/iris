import json
from generate_corpus import generate_corpus
from generate_qa_intents import generate_questions_and_intents
from process_text import extract_sentences
from web_scraper import fetch_website_content

def main(url):
    try:
        all_text = fetch_website_content(url)
        if not all_text:
            return {
                "status": "error",
                "message": f"No content found at {url}",
                "url": url
            }
            
        sentences = extract_sentences(all_text)
        qa_pairs = generate_questions_and_intents(sentences)
        corpus = generate_corpus(qa_pairs)
        
        return {
            "status": "success",
            "data": corpus,
            "url": url
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "url": url
        }

# USAGE
# url = 'https://example.com'
# corpus = main(url)
# print(corpus)