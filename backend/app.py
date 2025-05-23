from flask import Flask, request, jsonify, send_file, abort
from datrie_implementation.suffix_tree import build_suffix_tree, load_tree, save_tree
from datrie_implementation.db_tree import setup_database, store_occurrences
from datrie_implementation.index_books import index_books
from datrie_implementation.main import parse_emoji_regex
from flask_cors import CORS
import os
import re
import urllib.parse
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Paths
DATA_FILE = os.path.join(os.path.dirname(__file__), "moby_words.txt")
TREE_FILE = os.path.join(os.path.dirname(__file__), "suffix_tree.pkl")
BOOK_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Gutenberg_Books"))
DB_FILE = os.path.join(os.path.dirname(__file__), "searches.db")
LEAVES_DB = os.path.join(os.path.dirname(__file__), "leaves.db")

# --- Initialize database ---
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

# mapping‐DB holds your suffix→offset data
conn_tree, cursor_tree = setup_database(LEAVES_DB)

# --- Load or build suffix tree ---
if os.path.exists(TREE_FILE):
    trie, suffix_to_id = load_tree(TREE_FILE)
else:
    with open(DATA_FILE, "r") as f:
        words = f.read().splitlines()
    trie, suffix_to_id = build_suffix_tree(words)
    save_tree(trie, suffix_to_id, TREE_FILE)

# --- Search with emoji regex support ---
@app.route("/api/search", methods=["GET"])
def search():
    raw_query = request.args.get("q", "")
    raw_query = urllib.parse.unquote_plus(raw_query).strip()
    if not raw_query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    pattern = parse_emoji_regex(raw_query)
    if not pattern:
        return jsonify({"error": "Invalid emoji prefix or format."}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO recent_searches (query) VALUES (?)", (raw_query,))
    conn.commit()
    conn.close()

    if pattern.startswith("SENTENCE:") or pattern.startswith("SENTENCE_REGEX:"):
        return sentence_search_handler(pattern, raw_query)

    if pattern.startswith("RAW_REGEX:"):
        regex = pattern[len("RAW_REGEX:"):]
    else:
        regex = pattern

    try:
        compiled = re.compile(regex, re.IGNORECASE)
    except re.error as e:
        return jsonify({"error": f"Invalid regex pattern: {e}"}), 400

    results = []
    for filename in os.listdir(BOOK_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(BOOK_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read()

                matches = []
                for match in re.finditer(r'\b\w+\b', text):
                    word = match.group()
                    if compiled.search(word):
                        start = match.start()
                        snippet = text[max(0, start - 40): start + len(word) + 40]
                        matches.append({
                            "snippet": snippet.strip(),
                            "word": word
                        })

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
        "query": raw_query,
        "regex": regex,
        "emoji": raw_query.split(":", 1)[0] if ":" in raw_query else "",
        "results": results
    })

# --- Sentence-based search handler ---
def sentence_search_handler(pattern, raw_query):
    if pattern.startswith("SENTENCE:"):
        phrase = pattern[len("SENTENCE:"):].strip()
        regex = re.compile(re.escape(phrase), re.IGNORECASE)
    else:
        raw_regex = pattern[len("SENTENCE_REGEX:"):].strip()
        try:
            regex = re.compile(raw_regex, re.IGNORECASE)
        except re.error as e:
            return jsonify({"error": f"Invalid sentence regex pattern: {e}"}), 400

    results = []
    for filename in os.listdir(BOOK_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(BOOK_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    text = f.read()

                sentences = re.split(r'(?<=[\.!?])\s+', text)
                sentences = [s.strip() for s in sentences if s.strip()]
                matches = []
                for sentence in sentences:
                    if regex.search(sentence):
                        matches.append({"snippet": sentence.strip(), "word": ""})

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
        "query": raw_query,
        "regex": regex.pattern,
        "emoji": raw_query.split(":", 1)[0] if ":" in raw_query else "",
        "results": results
    })

# --- Get matches in a specific book ---
@app.route("/api/book/<path:book_name>", methods=["GET"])
def book_word_matches(book_name):
    query = request.args.get("word", "").strip()
    book_name = urllib.parse.unquote(book_name.strip())
    book_path = os.path.join(BOOK_FOLDER, book_name)

    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    with open(book_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()

    pattern = parse_emoji_regex(query)
    if not pattern or pattern.startswith("SENTENCE"):
        return jsonify({"book": book_name, "word": query, "matches": []})

    if pattern.startswith("RAW_REGEX:"):
        pattern = pattern[len("RAW_REGEX:"):]

    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return jsonify({"book": book_name, "word": query, "matches": []})

    matches = []
    for match in re.finditer(r'\b\w+\b', text):
        word = match.group()
        if compiled.search(word):
            start = match.start()
            context = text[max(0, start - 100): start + len(word) + 100]
            matches.append({"offset": start, "context": context.strip()})

    return jsonify({
        "book": book_name,
        "word": query,
        "matches": matches
    })

# --- ✅ Get full book text ---
@app.route("/api/book/full/<path:book_name>", methods=["GET"])
def get_full_book(book_name):
    book_name = urllib.parse.unquote(book_name.strip())
    base, ext = os.path.splitext(book_name)
    base = re.sub(r'[\s-]+$', '', base)
    book_name = base + ext
    book_path = os.path.join(BOOK_FOLDER, book_name)

    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    with open(book_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        text = f.read()

    return jsonify({
        "book": book_name,
        "text": text
    })

# --- List all books ---
@app.route("/api/books", methods=["GET"])
def get_books():
    if not os.path.exists(BOOK_FOLDER):
        return jsonify([])
    files = [f for f in os.listdir(BOOK_FOLDER) if f.endswith(".txt")]
    return jsonify(files)

# --- Recent search history ---
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

# --- Clear recent search history ---
@app.route("/api/clear", methods=["POST"])
def clear_recent_searches():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM recent_searches")
    conn.commit()
    conn.close()
    return jsonify({"message": "Recent searches cleared."})

# --- Upload .txt book ---
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

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True)
