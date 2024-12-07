from flask import Flask, request, jsonify
from validators import url as validate_url
from main import main
from functools import lru_cache
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def is_valid_url(url):
    return validate_url(url)

@lru_cache(maxsize=100)
def cached_main(url):
    return main(url)

@app.route('/', methods=['POST'])
def generate_corpus_route():
    data = request.get_json()
    url = data.get('url')

    if not url or not is_valid_url(url):
        return jsonify({'error': 'Please provide a valid URL'}), 400

    try:
        if app.config['CACHE_ENABLED']:
            corpus = cached_main(url)
        else:
            corpus = main(url)
        return jsonify(corpus), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
