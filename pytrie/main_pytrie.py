import os
import re
import timeit
import json
from collections import defaultdict
from suffix_pytrie import build_suffix_tree, save_tree, load_tree
from moby_words import load_moby_words
from db_pytrie import create_db, store_occurrences, search_word, is_database_populated, export_to_csv

BOOKS_FOLDER = "Gutenberg_Top_100"

def index_books(folder, trie, suffix_to_id):
    occurrences_map = defaultdict(lambda: defaultdict(list))
    next_leaf_id = max(suffix_to_id.values(), default=0) + 1

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if filename.endswith(".txt") and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tokens = re.findall(r"\b[a-z]+\b", f.read().lower())

                for offset, token in enumerate(tokens):
                    if token not in suffix_to_id:
                        suffix_to_id[token] = next_leaf_id
                        trie.insert(token, next_leaf_id)
                        next_leaf_id += 1
                    leaf_id = suffix_to_id[token]
                    occurrences_map[leaf_id][filename].append(offset)

                print(f"Indexed {len(tokens)} words from {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return occurrences_map

def main():
    create_db()

    # Load or build suffix trie
    trie, suffix_to_id = load_tree()
    if trie is None or suffix_to_id is None:
        print("[*] No saved suffix tree found. Building a new one...")
        words = load_moby_words()

        start_time = timeit.default_timer()
        trie, suffix_to_id = build_suffix_tree(words)
        duration = timeit.default_timer() - start_time
        print(f"[✓] Suffix trie built in {duration:.10f} seconds.")

        save_tree(trie, suffix_to_id)

    # Index books if DB is empty
    if not is_database_populated():
        print("[*] Indexing books...")
        start_time = timeit.default_timer()
        occurrences_map = index_books(BOOKS_FOLDER, trie, suffix_to_id)
        duration = timeit.default_timer() - start_time
        print(f"[✓] Books indexed in {duration:.10f} seconds.")

        store_occurrences(occurrences_map)
        export_to_csv()
        save_tree(trie, suffix_to_id)
    else:
        print("[✓] Database already populated. Skipping indexing.")

    # Interactive search with benchmarking
    while True:
        query = input("Enter a word to search (or 'exitfin' to quit): ").strip().lower()
        if query == "exitfin":
            break

        print(f"[*] Searching for '{query}' 10 times to measure speed...")

        timer = timeit.Timer(lambda: search_word(query, suffix_to_id))
        average_time = timer.timeit(number=10) / 10

        print(f"[✓] Average search time: {average_time:.6f} seconds.\n")

if __name__ == "__main__":
    main()
