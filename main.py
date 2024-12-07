import json
import generate_corpus
from generate_corpus import generate_corpus
from generate_qa_intents import generate_questions_and_intents
from process_text import extract_sentences
from web_scraper import fetch_website_content

def main(url):
    # Fetch and parse the website content
    all_text = fetch_website_content(url)
    # Extract sentences
    sentences = extract_sentences(all_text)
    # Generate Q&A pairs with intents
    qa_pairs = generate_questions_and_intents(sentences)
    # Generate the final corpus
    corpus = generate_corpus(qa_pairs)
    
    # with open('corpus.json', 'w') as f:
    #     json.dump(corpus, f, indent=4)

    return corpus

# USAGE
# url = 'https://example.com'
# corpus = main(url)
# print(corpus)