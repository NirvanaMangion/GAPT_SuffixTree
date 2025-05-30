from flask import Flask, request, jsonify
from datrie_implementation.suffix_tree import build_suffix_tree, load_tree, save_tree
from datrie_implementation.db_tree import setup_database, load_occurrences, store_occurrences, get_or_create_book_id
from datrie_implementation.index_books import index_books
from datrie_implementation.main import parse_emoji_regex, search_regex
from flask_cors import CORS, cross_origin
import os
import re
import urllib.parse
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

TREE_FILE = os.path.join(os.path.dirname(__file__), "suffix_tree.pkl")
BOOK_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Gutenberg_Books"))
LEAVES_DB = os.path.join(os.path.dirname(__file__), "leaves.db")
DB_FILE = os.path.join(os.path.dirname(__file__), "searches.db")

def get_book_id_to_name_map(cursor):
    cursor.execute("SELECT id, name FROM books")
    return {row[0]: row[1] for row in cursor.fetchall()}

def get_book_name_to_id_map(cursor):
    cursor.execute("SELECT id, name FROM books")
    return {row[1]: row[0] for row in cursor.fetchall()}

def extract_words_from_books(book_folder):
    word_set = set()
    for filename in os.listdir(book_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(book_folder, filename), "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().lower()
            words = re.findall(r'\b\w+\b', text)
            word_set.update(words)
    return list(word_set)

def setup_backend():
    conn, cursor = setup_database(LEAVES_DB)
    if os.path.exists(TREE_FILE) and os.path.exists(LEAVES_DB):
        trie, suffix_to_id = load_tree(TREE_FILE)
    else:
        words = extract_words_from_books(BOOK_FOLDER)
        trie, suffix_to_id = build_suffix_tree(words)
        save_tree(trie, suffix_to_id, TREE_FILE)
        print("Indexing all book occurrences. This might take a while...")
        occurrences_map, _ = index_books(BOOK_FOLDER, suffix_to_id, cursor)
        store_occurrences(cursor, occurrences_map)
        conn.commit()
        print("Indexed all books and saved suffix occurrences to the DB.")
    book_id_to_name = get_book_id_to_name_map(cursor)
    book_name_to_id = get_book_name_to_id_map(cursor)
    conn.close()
    return trie, suffix_to_id, book_id_to_name, book_name_to_id

trie, suffix_to_id, book_id_to_name, book_name_to_id = setup_backend()

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

    results = []
    emoji = raw_query.split(":", 1)[0] if ":" in raw_query else ""
    arg = raw_query.split(":", 1)[1].strip().lower() if ":" in raw_query else ""

    matching_keys = []

    if emoji in ["📄", "✏️", "📖", "📂", "📕", "📏", "🖌️", "📎", "🔧"]:
        try:
            if emoji == "📄":
                suffix = arg + "$"
                matching_keys = [k for k in trie.keys() if k.endswith(suffix)]

            elif emoji == "✏️":
                prefix = "#" + arg
                matching_keys = [k for k in trie.keys() if k.startswith(prefix) and k.endswith("$")]


            elif emoji == "📖":
                key = "#" + arg + "$"
                matching_keys = [key] if key in trie else []

            elif emoji == "📂":
                n = int(arg)
                matching_keys = [k for k in trie.keys() if k.startswith("#") and len(k) - 2 >= n]

            elif emoji == "📕":
                n = int(arg)
                matching_keys = [
                    k for k in trie.keys()
                    if k.startswith("#")
                    and len(k) - 2 <= n
                    and k[1:-1].isalpha()]
            elif emoji == "📏":
                n = int(arg)
                matching_keys = [k for k in trie.keys() if k.startswith("#") and len(k) - 2 == n]
                
            elif emoji == "🖌️":
                parts = [p.strip().rstrip('$') for p in arg.split("|")]
                matching_keys = [k for k in trie.keys() if any(k.endswith(part + "$") for part in parts)]

            elif emoji == "📎":
                if not arg.isdigit():
                    return jsonify({"error": "📎 expects a numeric value, e.g. 📎:2"}), 400
                count = int(arg)
                regex = re.compile(r'(.)\1{' + str(count - 1) + ',}')
                matching_keys = [k for k in trie.keys() if regex.search(k[1:-1] if k.startswith("#") else k)]

            elif emoji == "🔧":
                compiled = re.compile(arg)
                matching_keys = [k for k in trie.keys() if compiled.search(k[1:-1] if k.startswith("#") else k)]

        except Exception as e:
            return jsonify({"error": f"Failed to process search pattern: {e}"}), 400

        if not matching_keys:
            return jsonify({"results": [], "message": "No matches found."})

        conn, cursor = setup_database(LEAVES_DB)
        try:
            for key in matching_keys:
                if key not in suffix_to_id:
                    continue
                leaf_id = suffix_to_id[key]
                data = load_occurrences(cursor, leaf_id)

                for book_id, offsets in data.items():
                    book_name = book_id_to_name.get(int(book_id), f"Book {book_id}")
                    for offset in offsets[:10]:
                        try:
                            book_path = os.path.join(BOOK_FOLDER, book_name)
                            with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                                text = f.read()
                            start_offset = offset[1] if isinstance(offset, (list, tuple)) else offset
                            start = max(0, start_offset - 60)
                            end = min(len(text), start_offset + 60 )
                            snippet = text[start:end].replace('\n', ' ')
                            results.append({
                                "book": book_name,
                                "offset": offset,
                                "snippet": snippet
                            })
                        except Exception as e:
                            try:
                                print(f"[error] Reading {book_name} offset {offset}: {e}")
                            except Exception:
                                pass
        finally:
            conn.close()

        return jsonify({
            "query": raw_query,
            "emoji": emoji,
            "results": results
        })

    return regex_fallback_search(raw_query, pattern, emoji, arg)

# (Other route code stays unchanged, no edits required unless you're printing inside those too.)

def regex_fallback_search(raw_query, pattern, emoji, arg):
    results = []
    regex = None

    if pattern.startswith("SENTENCE:"):
        phrase = pattern[len("SENTENCE:"):].strip()
        regex = re.compile(re.escape(phrase), re.IGNORECASE)
    elif pattern.startswith("SENTENCE_REGEX:"):
        raw_regex = pattern[len("SENTENCE_REGEX:"):].strip()
        try:
            regex = re.compile(raw_regex, re.IGNORECASE)
        except re.error as e:
            return jsonify({"error": f"Invalid sentence regex pattern: {e}"}), 400
    else:
        try:
            regex = re.compile(arg, re.IGNORECASE)
        except re.error as e:
            return jsonify({"error": f"Invalid regex pattern: {e}"}), 400

    for filename in os.listdir(BOOK_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(BOOK_FOLDER, filename)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                if pattern.startswith("SENTENCE"):
                    sentences = re.split(r'(?<=[\.!?])\s+', text)
                    matches = [s for s in sentences if regex.search(s)]
                    for s in matches[:3]:
                        results.append({
                            "book": filename,
                            "offset": None,
                            "snippet": s
                        })
                else:
                    matches = [m for m in regex.finditer(text)]
                    for m in matches[:3]:
                        start, end = m.start(), m.end()
                        snippet = text[max(0, start-60):min(len(text), end+60)].replace('\n', ' ')
                        results.append({
                            "book": filename,
                            "offset": start,
                            "snippet": snippet
                        })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

    return jsonify({
        "query": raw_query,
        "emoji": emoji,
        "results": results
    })

@app.route("/api/books", methods=["GET"])
def get_books():
    if not os.path.exists(BOOK_FOLDER):
        return jsonify([])
    files = [f for f in os.listdir(BOOK_FOLDER) if f.endswith(".txt")]
    return jsonify(files)

@app.route("/api/book/full/<path:book_name>", methods=["GET"])
def get_full_book(book_name):
    book_name = urllib.parse.unquote(book_name.strip())
    book_path = os.path.join(BOOK_FOLDER, book_name)
    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404
    with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return jsonify({
        "book": book_name,
        "text": text
    })

@app.route("/api/book/<path:book_name>", methods=["GET"])
# @cross_origin()
def book_word_matches(book_name):
    query = request.args.get("word", "").strip()
    book_name = urllib.parse.unquote(book_name.strip())
    book_path = os.path.join(BOOK_FOLDER, book_name)
    if not os.path.exists(book_path):
        return jsonify({"error": "Book not found"}), 404

    # Get maps fresh from DB for up-to-date info
    conn, cursor = setup_database(LEAVES_DB)
    book_id_to_name = get_book_id_to_name_map(cursor)
    book_name_to_id = get_book_name_to_id_map(cursor)
    conn.close()

    book_id = book_name_to_id.get(book_name)
    pattern = parse_emoji_regex(query)
    if not pattern or pattern.startswith("SENTENCE") or book_id is None:
        return jsonify({"book": book_name, "word": query, "matches": []})

    results = []
    # 📄 Ends with a suffix
    if query.startswith("📄:"):
        conn, cursor = setup_database(LEAVES_DB)
        try:
            pattern = parse_emoji_regex(query)  # e.g. 'ing$'
            regex = re.compile(pattern, re.IGNORECASE)
            matching_keys = [k for k in trie.keys() if regex.search(k[1:-1])]
            if matching_keys:
                with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                for key in matching_keys:
                    leaf_id = suffix_to_id.get(key)
                    if not leaf_id: continue
                    data = load_occurrences(cursor, leaf_id)
                    offsets = data.get(str(book_id), []) if isinstance(data, dict) else []
                    for offset in offsets[:10]:
                        pos = offset[1] if isinstance(offset, (list, tuple)) else offset
                        start = max(0, pos - 240)
                        end = min(len(text), pos + 240)
                        snippet = text[start:end]
                        results.append({"offset": offset, "snippet": snippet})
        finally:
            conn.close()

    # ✏️ Starts with a prefix
    elif query.startswith("✏️:"):
        arg = query.split(":", 1)[1].strip().lower()  # ensure lowercase
        conn, cursor = setup_database(LEAVES_DB)
        try:
            # Find all trie keys that START with the prefix (whole word)
            matching_keys = [k for k in trie.keys() if k.startswith("#" + arg) and k.endswith("$")]
            if matching_keys:
                with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                for key in matching_keys:
                    leaf_id = suffix_to_id.get(key)
                    if not leaf_id:
                        continue
                    data = load_occurrences(cursor, leaf_id)
                    offsets = data.get(str(book_id), []) if isinstance(data, dict) else []
                    for offset in offsets[:10]:
                        pos = offset[1] if isinstance(offset, (list, tuple)) else offset
                        start = max(0, pos - 240)
                        end = min(len(text), pos + 240)
                        snippet = text[start:end]
                        results.append({"offset": offset, "snippet": snippet})
        finally:
            conn.close()


    # 📂 Minimum word length
    # 📂 Minimum word length
    elif query.startswith("📂:"):
        # 1) build the pattern
        pattern = parse_emoji_regex(query)  # e.g. r"\b\w{8,}\b"

        # 2) grab all occurrences in one shot
        conn, cursor = setup_database(LEAVES_DB)
        try:
            occ_map = search_regex(pattern, suffix_to_id, cursor)
            offsets = occ_map.get(str(book_id), [])
        finally:
            conn.close()

        # 3) read the book once
        with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # 4) slice out your snippets
        for off in offsets[:10]:
            pos = off[1] if isinstance(off, (list, tuple)) else off
            start = max(0, pos - 240)
            end = min(len(text), pos + 240)
            snippet = text[start:end]
            results.append({"offset": off, "snippet": snippet})

    # 📕 Maximum word length
    elif query.startswith("📕:"):
        pattern = parse_emoji_regex(query)
        conn, cursor = setup_database(LEAVES_DB)
        try:
            occ_map = search_regex(pattern, suffix_to_id, cursor)
            offsets = occ_map.get(str(book_id), [])
        finally:
            conn.close()

        with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        matches_added = 0
        for off in offsets:
            if matches_added >= 10:
                break
            pos = off[1] if isinstance(off, (list, tuple)) else off

            # Extract the actual word at position `pos`
            left = pos
            right = pos
            while left > 0 and text[left-1].isalpha():
                left -= 1
            while right < len(text) and text[right].isalpha():
                right += 1
            word = text[left:right]

            # Only add if the word is all alphabetic and of correct length
            if word.isalpha():
                start = max(0, pos - 240)
                end = min(len(text), pos + 240)
                snippet = text[start:end]
                results.append({"offset": off, "snippet": snippet})
                matches_added += 1

   # 📏 Exact word length
    elif query.startswith("📏:"):
        pattern = parse_emoji_regex(query)  # should be r"\b\w{N}\b"
        regex = re.compile(pattern)

        with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        count = 0
        for m in regex.finditer(text):
            pos = m.start()
            start = max(0, pos - 240)
            end = min(len(text), pos + 240)
            snippet = text[start:end]
            results.append({"offset": pos, "snippet": snippet})
            count += 1
            if count >= 10:   # limit to 10
         
                break


    # 🖌️ Ends in any listed suffix
    elif query.startswith("🖌️:"):
        conn, cursor = setup_database(LEAVES_DB)
        try:
            pattern = parse_emoji_regex(query)  # e.g. '(ing|ed)$'
            regex = re.compile(pattern, re.IGNORECASE)
            matching_keys = [k for k in trie.keys() if regex.search(k[1:-1])]
            if matching_keys:
                with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                for key in matching_keys:
                    leaf_id = suffix_to_id.get(key)
                    if not leaf_id:
                        continue
                    data = load_occurrences(cursor, leaf_id)
                    offsets = data.get(str(book_id), []) if isinstance(data, dict) else []
                    for offset in offsets[:10]:
                        pos = offset[1] if isinstance(offset, (list, tuple)) else offset
                        start = max(0, pos - 240)
                        end = min(len(text), pos + 240)
                        snippet = text[start:end]
                        results.append({"offset": offset, "snippet": snippet})
        finally:
            conn.close()


    # 📎 Repeated characters
    elif query.startswith("📎:"):
        conn, cursor = setup_database(LEAVES_DB)
        try:
            pattern = parse_emoji_regex(query)  # e.g. '(.)\1{2,}'
            regex = re.compile(pattern)
            matching_keys = [k for k in trie.keys() if regex.search(k[1:-1])]
            if matching_keys:
                with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                for key in matching_keys:
                    leaf_id = suffix_to_id.get(key)
                    if not leaf_id: continue
                    data = load_occurrences(cursor, leaf_id)
                    offsets = data.get(str(book_id), []) if isinstance(data, dict) else []
                    for offset in offsets[:10]:
                        pos = offset[1] if isinstance(offset, (list, tuple)) else offset
                        start = max(0, pos - 240)
                        end = min(len(text), pos + 240)
                        snippet = text[start:end]
                        results.append({"offset": offset, "snippet": snippet})
        finally:
            conn.close()

    # 📖 Exact word match
    elif query.startswith("📖:"):
        conn, cursor = setup_database(LEAVES_DB)
        try:
            word = query.split(":", 1)[1].strip().lower()
            key = "#" + word + "$"
            if key in suffix_to_id:
                leaf_id = suffix_to_id[key]
                data = load_occurrences(cursor, leaf_id)
                offsets = data.get(str(book_id), []) if isinstance(data, dict) else []
                with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                for offset in offsets[:10]:
                    start_offset = offset[1] if isinstance(offset, (list, tuple)) else offset
                    start = max(0, start_offset - 240)
                    end = min(len(text), start_offset + 240)
                    snippet = text[start:end]
                    results.append({"offset": offset, "snippet": snippet})
        finally:
            conn.close()

    # 🔧 Raw custom regex
    elif query.startswith("🔧:"):
        conn, cursor = setup_database(LEAVES_DB)
        try:
            pattern = parse_emoji_regex(query)  # raw regex after 'RAW_REGEX:'
            regex = re.compile(pattern, re.IGNORECASE)
            with open(book_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            for m in regex.finditer(text):
                pos = m.start()
                start = max(0, pos - 240)
                end = min(len(text), pos + 240)
                snippet = text[start:end]
                results.append({"offset": pos, "snippet": snippet})
        finally:
            conn.close()

    resp = jsonify({"book": book_name, "word": query, "matches": results})
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp

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
