from flask import Flask, request, jsonify
from validators import url as validate_url
from main import main
from functools import lru_cache
from config import Config
import requests

app = Flask(__name__)
app.config.from_object(Config)

def is_valid_url(url):
    return validate_url(url)

@lru_cache(maxsize=100)
def cached_main(url):
    return main(url)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Online",
        "message": "Iris API is running",
        "version": "1.0"
    })

@app.route('/', methods=['POST'])
def generate_corpus_route():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
        
    if not is_valid_url(url):
        return jsonify({"error": "Invalid URL format"}), 400
        
    try:
        result = cached_main(url)
        return jsonify(result)
    except requests.exceptions.RequestException:
        return jsonify({"error": f"Could not connect to '{url}'"}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/git', methods=['POST'])
def git_webhook():
    import subprocess
    subprocess.run(['git', 'pull'], cwd='/var/www/iris')
    subprocess.run(['systemctl', 'restart', 'iris'])
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)