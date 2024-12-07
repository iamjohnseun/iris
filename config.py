import os

class Config:
    DEBUG = os.getenv('DEBUG', False)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    SCRAPING_MAX_DEPTH = int(os.getenv('SCRAPING_MAX_DEPTH', 10))
    SCRAPING_DELAY = float(os.getenv('SCRAPING_DELAY', 1.0))
    REQUEST_TIMEOUT = (5, 15)  # (Connect timeout, Read timeout)
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', True)
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # 1 hour
