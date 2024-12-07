from flask import Flask, request, make_response, jsonify
import json
from main import main

app = Flask(__name__)

@app.route('/', methods=['POST'])
def generate_corpus_route():
    url = request.json.get('url')

    if not url:
        return make_response(jsonify({'error': 'URL is required'}), 400)

    try:
        corpus = main(url)
        return make_response(jsonify(corpus), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True)
