import json
from sphinx.generate_corpus import generate_corpus
from sphinx.generate_qa_intents import generate_questions_and_intents
from sphinx.process_text import extract_sentences
from sphinx.web_scraper import fetch_website_content, parse_website_content

def main(url):
    html_content = fetch_website_content(url)
    parsed_content = parse_website_content(html_content)
    sentences = extract_sentences(parsed_content)
    qa_pairs = generate_questions_and_intents(sentences)
    corpus = generate_corpus(qa_pairs)
    
    # with open('corpus.json', 'w') as f:
    #     json.dump(corpus, f, indent=4)

    return corpus
