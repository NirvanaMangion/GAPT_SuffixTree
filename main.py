import os
import re
import json
import sqlite3
import timeit
from collections import defaultdict
from suffix_tree import build_suffix_tree, save_tree, load_tree
from db_tree import create_database, store_occurrences, load_occurrences, open_database

def load_word_list(filename="words.txt"):
    """Loads a list of words from a file."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def index_books(folder, suffix_to_id):
    """Indexes books and maps word positions to suffix IDs."""
    occurrences_map = defaultdict(lambda: defaultdict(list))
    word_pattern = re.compile(r"\w+")

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                tokens = word_pattern.findall(f.read().lower())

            for offset, token in enumerate(tokens):
                leaf_id = suffix_to_id.get(token)
                if leaf_id is not None:
                    occurrences_map[leaf_id][filename].append(offset)

    return occurrences_map

def search_word(word, suffix_to_id, cursor):
    """Searches for a word in the suffix tree and retrieves occurrences."""
    leaf_id = suffix_to_id.get(word.strip().lower())
    if leaf_id:
        return load_occurrences(cursor, leaf_id)
    return {}

def main():
    """Main function to coordinate suffix tree creation, indexing, and searching."""
    db_name = "suffix_tree.db"
    create_database(db_name)
    conn, cursor = open_database(db_name)

    # Load or build suffix tree
    word_list = load_word_list()

    print("[*] Building suffix tree...")
    start_time = timeit.default_timer()
    suffix_tree, suffix_to_id = build_suffix_tree(word_list)
    build_duration = timeit.default_timer() - start_time
    print(f"[+] Suffix tree built in {build_duration:.10f} seconds.")

    save_tree(suffix_tree, suffix_to_id)

    # Index books and store occurrences
    folder = "Gutenberg_Top_100"
    print("[*] Indexing books...")
    start_time = timeit.default_timer()
    occurrences_map = index_books(folder, suffix_to_id)
    indexing_duration = timeit.default_timer() - start_time
    print(f"[+] Books indexed in {indexing_duration:.10f} seconds.")

    store_occurrences(cursor, occurrences_map)
    conn.commit()

    # User input for search
    search_term = input("Enter a word to search for: ").strip().lower()

    print("[*] Searching (measuring average of 10 runs)...")
    timer = timeit.Timer(lambda: search_word(search_term, suffix_to_id, cursor))
    search_duration = timer.timeit(number=10) / 10
    results = search_word(search_term, suffix_to_id, cursor)
    print(f"[+] Average search time: {search_duration:.6f} seconds.")
    print(f"Occurrences of '{search_term}':", json.dumps(results, indent=4))

    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
