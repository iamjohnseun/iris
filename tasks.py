import os
import json
import uuid
import gc
import torch
from config import Config
from urllib.parse import urlparse
from celery_config import celery_app
from web_scraper import get_urls_to_process, process_batch, check_memory_usage
from generate_qa_intents import get_model, clean_text
from generate_utterances import get_paraphrase_model
from main import main

def get_output_filename(url, job_id):
    domain = urlparse(url).netloc or 'local'
    return f"{domain}-{job_id}.json"

@celery_app.task(bind=True)
def process_website_task(self, url, single_page=False):
    # Create download directory if it doesn't exist
    os.makedirs('download', exist_ok=True)
    
    job_id = str(uuid.uuid4())[:8]
    output_file = get_output_filename(url, job_id)
    output_path = os.path.join('download', output_file)
    
    # Determine URLs to process
    urls = get_urls_to_process(url, single_page)
    total_urls = len(urls)
    
    # Decide between synchronous and asynchronous processing
    if single_page or total_urls <= Config.SYNCHRONOUS_THRESHOLD:
        # Process synchronously using main.py
        result = main(url, single_page=single_page)
        
        # Save the result to a JSON file
        with open(output_path, 'w') as f:
            json.dump(result['data'], f, indent=4)
        
        # Add additional properties to the result
        result.update({
            'filename': output_file,
            'url': f"{Config.APP_URL}/download/{output_file}",
            'task_id': self.request.id,
            'status_url': f"{Config.APP_URL}/status/{self.request.id}",
            'total_processed': total_urls,
            'total_qa_pairs': len(result.get('data', []))
        })
        
        return result
    
    else:
        # Process asynchronously
        batch_size = 10
        processed_pages = 0
        all_results = []
        
        qa_model = get_model()
        paraphrase_model = get_paraphrase_model()
        
        try:
            for i in range(0, len(urls), batch_size):
                if check_memory_usage() >= Config.MAX_MEMORY_USAGE:
                    gc.collect()
                    torch.cuda.empty_cache()
                    
                batch = urls[i:i + batch_size]
                batch_results = process_batch(batch)
                
                # Generate QA pairs for batch
                qa_pairs = []
                for page in batch_results:
                    cleaned_text = clean_text(page['content'])
                    qa_response = qa_model(f"Generate different frequently asked questions (FAQ's) and answers from: {cleaned_text}")
                    qa_pairs.extend(qa_response)
                
                # Append QA pairs to all_results
                all_results.extend(qa_pairs)
                
                # Save intermediate results
                with open(output_path, 'w') as f:
                    json.dump(all_results, f, indent=4)
                
                processed_pages += len(batch)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed_pages,
                        'total': total_urls,
                        'status': f'Processing batch {i//batch_size + 1} of {(total_urls + batch_size - 1)//batch_size}',
                        'url': f"{Config.APP_URL}/download/{output_file}",
                        'task_id': self.request.id,
                        'status_url': f"{Config.APP_URL}/status/{self.request.id}"
                    }
                )
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'task_id': self.request.id,
                'status_url': f"{Config.APP_URL}/status/{self.request.id}"
            }
                
        finally:
            # Cleanup
            del qa_model
            del paraphrase_model
            gc.collect()
            torch.cuda.empty_cache()
        
        return {
            'status': 'complete',
            'filename': output_file,
            'url': f"{Config.APP_URL}/download/{output_file}",
            'task_id': self.request.id,
            'status_url': f"{Config.APP_URL}/status/{self.request.id}",
            'total_processed': processed_pages,
            'total_qa_pairs': len(all_results)
        }
