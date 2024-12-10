# Chromesque Iris 🤖

## What is Chromesque Iris?
Chromesque Iris is a powerful AI-driven content processing system that transforms website content into structured training data for conversational AI. By combining advanced web scraping, natural language processing, and state-of-the-art language models, it automatically generates high-quality question-answer pairs and varied utterances perfect for training chatbots and AI assistants.

Think of it as your AI content curator - it reads websites like a human would, understands the content, and creates natural conversations around it.

## ✨ Key Features
- 🕷️ Intelligent web crawling with robots.txt compliance
- 🧠 Advanced NLP using transformer models
- 💬 Dynamic question-answer pair generation
- 🎯 Automatic intent classification
- 🔄 Natural language paraphrasing
- 📊 Memory-efficient processing
- 🚀 RESTful API interface

## 🛠️ Technical Stack
- Python 3.x
- Flask
- Hugging Face Transformers (T5 models)
- NLTK
- BeautifulSoup4
- PyTorch
- psutil for resource management

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/iamjohnseun/iris.git
```

2. Install dependencies:
pip install -r requirements.txt

3. Set up NLTK data:
python -m nltk.downloader punkt

##  💻 Usage Examples
### 🌐 Using  the API
```bash
import requests

response = requests.post('http://localhost:5000', 
    json={
        'url': 'https://example.com',
        'single_page': False
    }
)
```
### 📊 Output Format
```json
{
    "status": "complete",
    "data": [
        {
            "intent": "faq.business_hours",
            "utterances": [
                "What time are you open?",
                "When does the business open?",
                "Tell me your operating hours"
            ],
            "answer": ["We're open 9-5 Monday through Friday"]
        }
    ],
    "stats": {
        "pages_processed": 1,
        "questions_generated": 10,
        "processing_time": "2.3s"
    },
    "url": "https://example.com",
    "errors": []
}
```
## 🔧 Core Components
### 🌐 Web Scraper
- Smart content extraction
- Respects website crawling rules
- Handles pagination and navigation
- Memory-efficient processing

### 🪢 Text Processor
- Intelligent sentence segmentation
- Context-aware content extraction
- Multi-path NLTK data handling

### 🤖 Question Generator
- T5 transformer-based generation
- Dynamic intent classification
- Efficient model management

### 💬 Utterance Generator
- Natural language paraphrasing
- Training data augmentation
- Memory-optimized model handling

### ⚙️ Configuration
Key settings in config.py:

- Model parameters
- Memory thresholds
- API configurations
- NLTK data paths

### 🎯 Best Practices
- Start with single_page=True for testing
- Monitor memory usage for large websites
- Implement rate limiting in production
- Use garbage collection for long processes
- Regular model cleanup after processing

### 🤝 Contributing
We welcome contributions! Reach out to me john@chromesque.com for collaboration.

### 📜 License
This project is licensed under the MIT License.