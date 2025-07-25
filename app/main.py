from flask import Flask, request, jsonify, redirect, url_for
from app.models import create_mapping, get_mapping, increment_click, short_code_exists
from app.utils import generate_short_code, is_valid_url

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "service": "URL Shortener API"})

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400
    long_url = data["url"]
    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400
    for _ in range(10):
        code = generate_short_code()
        if not short_code_exists(code):
            create_mapping(code, long_url)
            short_url = request.host_url.rstrip('/') + '/' + code
            return jsonify({"short_code": code, "short_url": short_url}), 201
    return jsonify({"error": "Could not generate unique code"}), 500

@app.route('/<short_code>')
def redirect_short_code(short_code):
    mapping = get_mapping(short_code)
    if not mapping:
        return jsonify({"error": "Not found"}), 404
    increment_click(short_code)
    return redirect(mapping["original_url"], code=302)

@app.route('/api/stats/<short_code>')
def stats(short_code):
    mapping = get_mapping(short_code)
    if not mapping:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "url": mapping["original_url"],
        "clicks": mapping["click_count"],
        "created_at": mapping["created_at"]
    })
