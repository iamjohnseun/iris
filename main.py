import json
from generate_corpus import generate_corpus
from generate_qa_intents import generate_questions_and_intents
from process_text import extract_sentences
from web_scraper import fetch_website_content

def main(url):
    result = {
        "status": "processing",
        "data": None,
        "stats": {},
        "url": url,
        "errors": []
    }

    try:
        # Yield initial status
        yield json.dumps({"status": "processing", "message": "Fetching website content."})

        scraped_content = fetch_website_content(url)
        result["stats"] = scraped_content["stats"]

        # Yield after fetching content
        yield json.dumps({"status": "processing", "message": "Website content fetched. Extracting sentences."})

        if not scraped_content["content"]:
            result["status"] = "error"
            result["errors"].append("No content found.")
            yield json.dumps(result)
            return

        sentences = extract_sentences(scraped_content["content"])

        if sentences:
            # Yield after extracting sentences
            yield json.dumps({"status": "processing", "message": f"{len(sentences)} sentences extracted. Generating QA pairs."})

            qa_pairs = generate_questions_and_intents(sentences)

            if qa_pairs:
                # Yield after generating QA pairs
                yield json.dumps({"status": "processing", "message": f"{len(qa_pairs)} QA pairs generated. Generating corpus."})

                corpus = generate_corpus(qa_pairs)
                result["data"] = corpus
                result["status"] = "complete"
                result["message"] = "Corpus generated successfully."
                # Yield the final result
                yield json.dumps(result)
            else:
                result["status"] = "error"
                result["errors"].append("No QA pairs generated.")
                yield json.dumps(result)
        else:
            result["status"] = "error"
            result["errors"].append("No sentences extracted.")
            yield json.dumps(result)

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        yield json.dumps(result)

# USAGE
# url = 'https://example.com'
# corpus = main(url)
# print(corpus)