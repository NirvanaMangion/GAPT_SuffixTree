from flask import Flask, request, jsonify
from datrie_implementation.suffix_tree import build_suffix_tree, load_tree, save_tree
from flask_cors import CORS
import os
import re
import urllib.parse
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename  # ✅ added for safe file saving

app = Flask(__name__)
CORS(app)

DATA_FILE = "backend/moby_words.txt"
TREE_FILE = "backend/suffix_tree.pkl"
BOOK_FOLDER = "backend/books/"
DB_FILE = "backend/searches.db"

# Create DB and table if not exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recent_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Load or build suffix tree
if os.path.exists(TREE_FILE):
    trie, suffix_to_id = load_tree(TREE_FILE)
else:
    with open(DATA_FILE, "r") as f:
        words = f.read().splitlines()
    trie, suffix_to_id = build_suffix_tree(words)
    save_tree(trie, suffix_to_id, TREE_FILE)

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip().lower()
    print("QUERY:", query)

    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    # Store the search in SQLite
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO recent_searches (query) VALUES (?)", (query,))
    conn.commit()
    conn.close()

    # Search across all books
    results = []
    for filename in os.listdir(BOOK_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(BOOK_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read()

                matches = []
                for match in re.finditer(rf'\b{re.escape(query)}\b', text, re.IGNORECASE):
                    start = match.start()
                    context = text[max(0, start - 30): start + len(query) + 30]
                    matches.append(context.strip())

                if matches:
                    results.append({
                        "book": filename,
                        "count": len(matches),
                        "snippets": matches[:3]
                    })

            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

    return jsonify({
        "query": query,
        "results": results
    })

@app.route("/api/word/<word>", methods=["GET"])
def word_info(word):
    word = word.strip().lower()
    book_data = {}

    if not os.path.exists(BOOK_FOLDER):
        return jsonify({"error": "Book folder not found."}), 500

    for filename in os.listdir(BOOK_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(BOOK_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read().lower()
                    count = len(re.findall(rf'\b{re.escape(word)}\b', text))
                    if count > 0:
                        book_data[filename] = count
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

    result = [{"title": title, "frequency": freq} for title, freq in book_data.items()]
    return jsonify({"word": word, "books": result})

@app.route("/api/book/<path:book_name>", methods=["GET"])
def book_word_matches(book_name):
    word = request.args.get("word", "").strip().lower()
    book_name = urllib.parse.unquote(book_name.strip())

    book_path = os.path.join(BOOK_FOLDER, book_name)
    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    with open(book_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()

    matches = []
    for match in re.finditer(rf'\b{re.escape(word)}\b', text, re.IGNORECASE):
        start_index = match.start()
        context = text[max(0, start_index - 30): start_index + len(word) + 30]
        matches.append({"offset": start_index, "context": context})

    return jsonify({
        "book": book_name,
        "word": word,
        "matches": matches
    })

@app.route("/api/book/full/<path:book_name>", methods=["GET"])
def get_full_book(book_name):
    word = request.args.get("word", "").strip().lower()
    book_name = urllib.parse.unquote(book_name.strip())
    book_path = os.path.join(BOOK_FOLDER, book_name)

    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    with open(book_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()

    return jsonify({
        "book": book_name,
        "word": word,
        "text": text
    })

@app.route("/api/books", methods=["GET"])
def get_books():
    if not os.path.exists(BOOK_FOLDER):
        return jsonify([])
    files = [f for f in os.listdir(BOOK_FOLDER) if f.endswith(".txt")]
    return jsonify(files)

@app.route("/api/recent", methods=["GET"])
def get_recent_searches():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT query, timestamp
        FROM recent_searches
        ORDER BY id DESC
        LIMIT 10
    """)
    results = [{"query": row[0], "timestamp": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(results)

@app.route("/api/clear", methods=["POST"])
def clear_recent_searches():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM recent_searches")
    conn.commit()
    conn.close()
    return jsonify({"message": "Recent searches cleared."})

# ✅ NEW: Upload endpoint
@app.route("/api/upload", methods=["POST"])
def upload_book():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".txt"):
        return jsonify({"error": "Only .txt files allowed."}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(BOOK_FOLDER, filename)
    file.save(save_path)

    return jsonify({"message": f"{filename} uploaded successfully."})

if __name__ == "__main__":
    app.run(debug=True)
