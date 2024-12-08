from flask import Flask, request, jsonify
from validators import url as validate_url
from main import main
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def is_valid_url(url):
    if not url:
        return False
    return validate_url(url)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "Iris API is running",
        "version": "1.0"
    })

@app.route('/', methods=['POST'])
def generate_corpus_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error", 
                "message": "Request body is required"
            }), 400
            
        url = data.get('url')
        if not is_valid_url(url):
            return jsonify({
                "status": "error", 
                "message": "Invalid or missing URL in request"
            }), 400
            
        result = main(url)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/git', methods=['POST'])
def git_webhook():
    try:
        import subprocess
        subprocess.run(['git', 'pull'], cwd='/var/www/iris')
        subprocess.run(['systemctl', 'restart', 'iris'])
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
