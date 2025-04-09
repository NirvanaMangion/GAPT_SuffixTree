from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

BOOKS_DIR = "Gutenberg_Top_100"
books = {}  # book_id -> {title, content}

# Load books into memory
def load_books():
    for idx, filename in enumerate(os.listdir(BOOKS_DIR)):
        if filename.endswith(".txt"):
            with open(os.path.join(BOOKS_DIR, filename), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                books[str(idx)] = {
                    "title": filename.replace(".txt", ""),
                    "content": content
                }

@app.route('/search')
def search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    results = []
    for book_id, book in books.items():
        if query in book["content"]:
            count = book["content"].count(query)
            results.append({
                "book_id": book_id,
                "title": book["title"],
                "matches": count
            })

    return jsonify(results)

if __name__ == '__main__':
    load_books()
    app.run(debug=True)
