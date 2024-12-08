import json
from generate_corpus import generate_corpus
from generate_qa_intents import generate_questions_and_intents
from process_text import extract_sentences
from web_scraper import fetch_website_content

def main(url):
    result = {
        "status": "partial",
        "data": None,
        "stats": {},
        "url": url,
        "errors": []
    }
    
    try:
        scraped_content = fetch_website_content(url)
        result["stats"]["crawl_stats"] = scraped_content["stats"]
        
        if not scraped_content["content"]:
            result["status"] = "error"
            result["errors"].append(f"No content found at {url}")
            return result
            
        sentences = extract_sentences(scraped_content["content"])
        
        try:
            qa_pairs = generate_questions_and_intents(sentences)
            corpus = generate_corpus(qa_pairs)
            result["data"] = corpus
            result["status"] = "success"
        except Exception as e:
            result["errors"].append(f"Processing error: {str(e)}")
            
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        
    return result

# USAGE
# url = 'https://example.com'
# corpus = main(url)
# print(corpus)