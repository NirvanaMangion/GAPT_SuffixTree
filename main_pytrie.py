import os
import re
from collections import defaultdict
from suffix_pytrie import build_suffix_tree, save_tree, load_tree
from db_pytrie import create_db, store_occurrences, search_word, is_database_populated, export_to_csv

BOOKS_FOLDER = "Gutenberg_Top_100"  # Books Folders

def index_books(folder, suffix_to_id):
    """
    Reads books, tokenizes content, and records word positions.
    Stores occurrences using leaf IDs mapped from the suffix tree.
    """
    occurrences_map = defaultdict(lambda: defaultdict(list))

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if filename.endswith(".txt") and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tokens = re.findall(r"\b[a-z]+\b", f.read().lower())  # Tokenize words
                
                for offset, token in enumerate(tokens):
                    leaf_id = suffix_to_id.get(token)
                    if leaf_id:
                        occurrences_map[leaf_id][filename].append(offset)  # Store word position

                print(f"Indexed {len(tokens)} words from {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return occurrences_map

# Create database
create_db()

# Load or build the suffix tree
trie, suffix_to_id = load_tree()

if trie is None or suffix_to_id is None:
    print("No saved suffix tree found. Building a new one...")
    words = set()
    for filename in os.listdir(BOOKS_FOLDER):
        file_path = os.path.join(BOOKS_FOLDER, filename)
        if filename.endswith(".txt") and os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                words.update(re.findall(r"\b[a-z]+\b", f.read().lower()))

    trie, suffix_to_id = build_suffix_tree(words)
    save_tree(trie, suffix_to_id)

# Only index books if the database is empty
if not is_database_populated():
    print("Indexing books...")
    occurrences_map = index_books(BOOKS_FOLDER, suffix_to_id)
    store_occurrences(occurrences_map)
    export_to_csv()  # Exporting database to CSV
else:
    print("Database already populated. Skipping indexing.")

# Interactive search loop
while True:
    search_query = input("Enter a word to search (or 'exitfin' to quit): ").strip()
    if search_query.lower() == "exitfin":
        break
    search_word(search_query, suffix_to_id)
