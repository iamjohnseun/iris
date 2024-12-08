from generate_corpus import generate_corpus
from generate_qa_intents import generate_questions_and_intents
from process_text import extract_sentences
from web_scraper import fetch_website_content

def main(url, single_page=False):
    result = {
        "status": "partial",
        "data": None,
        "stats": {},
        "url": url,
        "errors": []
    }
    
    try:
        scraped_content = fetch_website_content(url, single_page=single_page)
        result["stats"] = scraped_content["stats"]
        
        if not scraped_content["content"]:
            result["status"] = "error"
            result["errors"].append("No content found")
            return result
            
        sentences = extract_sentences(scraped_content["content"])
        print(f"Extracted {len(sentences)} sentences.")
        if sentences:
            qa_pairs = generate_questions_and_intents(sentences, url)
            if qa_pairs:
                corpus = generate_corpus(qa_pairs)
                result["data"] = corpus
                result["status"] = "complete"
            else:
                result["errors"].append("No QA pairs generated")
        else:
            result["errors"].append("No sentences extracted")
            
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        
    return result

# USAGE
# url = 'https://example.com'
# corpus = main(url)
# print(corpus)