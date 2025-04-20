from flask import Flask, request, jsonify
from datrie_implementation.suffix_tree import build_suffix_tree, load_tree, save_tree
from flask_cors import CORS
import os
import re
import urllib.parse  # ✅ for decoding book names from URL

app = Flask(__name__)
CORS(app)

DATA_FILE = "backend/moby_words.txt"
TREE_FILE = "backend/suffix_tree.pkl"
BOOK_FOLDER = "backend/books/"

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

    matches = trie.keys(query)
    print("MATCHES:", matches)

    cleaned_matches = [key.strip("#$") for key in matches]

    return jsonify({
        "query": query,
        "matches": cleaned_matches
    })


@app.route("/api/word/<word>", methods=["GET"])
def word_info(word):
    word = word.strip().lower()
    print(f"Checking word: {word}")
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
                    print(f"  {filename}: {count}")
                    if count > 0:
                        book_data[filename] = count
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

    result = [{"title": title, "frequency": freq} for title, freq in book_data.items()]
    return jsonify({"word": word, "books": result})


# ✅ Use <path:book_name> to allow slashes/encoded characters
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


if __name__ == "__main__":
    app.run(debug=True)
