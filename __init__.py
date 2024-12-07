from .config import Config
from .main import main
from .web_scraper import fetch_website_content
from .process_text import extract_sentences
from .generate_qa_intents import generate_questions_and_intents
from .generate_utterances import generate_utterances
from .generate_corpus import generate_corpus

__version__ = '1.0.0'
