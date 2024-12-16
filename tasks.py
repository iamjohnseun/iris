import json
import os
import time
from celery_config import celery_app
from config import Config
from main import main
from generate_qa_intents import get_model
from urllib.parse import urlparse

def get_output_filename(url, job_id):
    domain = urlparse(url).netloc.replace('www.', '') or 'local'
    return f"{domain}-{job_id}.json"

@celery_app.task(bind=True)
def process_website_task(self, url, single_page=False):
    steps = [
        "Setting up task",
        "Initializing models",
        "Fetching website content",
        "Processing content",
        "Generating Q&A pairs",
        "Saving results"
    ]
    total_steps = len(steps)
    
    try:
        # Step 1: Create directory structure
        self.update_state(
            state='STARTED',
            meta={
                'status': steps[0],
                'current': 1,
                'total': total_steps,
                'url': url
            }
        )
        
        # Create filename with domain and task ID
        filename = get_output_filename(url, self.request.id)
        
        # Create output directory
        output_dir = os.path.join('download', filename)
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 2: Initialize model
        self.update_state(
            state='STARTED',
            meta={
                'status': steps[1],
                'current': 2,
                'total': total_steps,
                'url': url
            }
        )
        model = get_model()
        
        generation_start_time = time.time()
        
        # Step 3-5: Process using main function
        self.update_state(
            state='STARTED',
            meta={
                'status': "Processing website content",
                'current': 3,
                'total': total_steps,
                'url': url
            }
        )
        
        result = main(url, single_page)
        # Add generation time to stats
        result['stats']['generation_time'] = time.time() - generation_start_time
        
        # Step 6: Save results with new filename
        self.update_state(
            state='STARTED',
            meta={
                'status': steps[5],
                'current': 6,
                'total': total_steps,
                'url': url
            }
        )
        
        output_file = os.path.join(output_dir, filename)
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
            
        return {
            'status': 'completed',
            'result': result,
            'result_url': f"{Config.APP_URL}/{output_file}",
            'url': url,
            'stats': result.get('stats', {})
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'url': url
        }
