import os

class Config:
    DEBUG = os.getenv('DEBUG', False)
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB
    MAX_QUESTION_LENGTH = 50 # Maximum length of a question
    MAX_BATCH_SIZE = 4 # Maximum number of questions to process in a single batch
    TORCH_THREADS = 2 # Number of threads for PyTorch
    MEMORY_THRESHOLD = 0.8  # 80% memory usage threshold
    FALLBACK_MODE = True  # Enable fallback processing
    MIN_SENTENCES = 10  # Minimum sentences to process
    MAX_SENTENCES = 100 # Maximum number of sentences to generate
    SCRAPING_MAX_DEPTH = int(os.getenv('SCRAPING_MAX_DEPTH', 10))
    SCRAPING_DELAY = float(os.getenv('SCRAPING_DELAY', 1.0))
    SCRAPING_DELAY_MAX = float(os.getenv('SCRAPING_DELAY_MAX', 3.0))  # Maximum delay for random backoff
    REQUEST_TIMEOUT = (5, 15)  # (Connect timeout, Read timeout)
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', True)
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # 1 hour
    
    # Content extraction configuration
    CONTENT_TAGS = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section']
    
    # User agent for the bot
    USER_AGENT = 'Mozilla/5.0 (compatible; IrisBot/1.0)'
    
    # File extensions to skip
    SKIP_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', 
                      '.xls', '.xlsx', '.zip', '.rar', '.exe', '.mp3', '.mp4')
