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
    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid URL"}), 400
    result = cached_main(url)
    return jsonify(result)

@app.route('/git', methods=['POST'])
def git_webhook():
    import subprocess
    subprocess.run(['git', 'pull'], cwd='/var/www/iris')
    subprocess.run(['systemctl', 'restart', 'iris'])
    return jsonify({"status": "updated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)