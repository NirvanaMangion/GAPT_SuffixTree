import os
import re
from collections import defaultdict

from suffix_tree import build_suffix_tree, save_tree, load_tree
from db_tree import setup_database,get_or_create_book_id, store_occurrences, load_occurrences
from moby_words import load_moby_words

def index_books(folder, suffix_to_id, cursor):
    """
    For each .txt file in 'folder', tokenize text and record offsets.
    Instead of using file names, this function obtains a numeric book ID for each file.
    Returns an occurrences_map of the form:
      { leaf_id: { book_id: [offsets...], ... }, ... }
    """
    occurrences_map = defaultdict(lambda: defaultdict(list))

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            print(f"Indexing {filename} ...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
                continue

            # Get or create a numeric book ID for the current file.
            book_id = get_or_create_book_id(cursor, filename)
            tokens = re.findall(r"\w+", text.lower())
            for token_index, token in enumerate(tokens):
                # Process the full word with '#' and '$'
                full_word = '#' + token + '$'
                leaf_id = suffix_to_id.get(full_word)
                if leaf_id:
                    occurrences_map[leaf_id][book_id].append(token_index)
                # Process proper suffixes
                for i in range(1, len(token) + 1):
                    suffix = token[i:] + '$'
                    leaf_id = suffix_to_id.get(suffix)
                    if leaf_id:
                        occurrences_map[leaf_id][book_id].append(token_index + i)
    return occurrences_map

def search_word(word, suffix_to_id, cursor):
    """
    Search for a given suffix in the JSON-based mapping.
    Uses load_occurrences_json() to load data from the DB, combines offsets,
    and prints results using the numeric book IDs.
    """
    word = word.strip().lower()
    full_key = '#' + word + '$'
    suffix_key = word + '$'
    keys_found = []

    if full_key in suffix_to_id:
        keys_found.append(full_key)
    if suffix_key in suffix_to_id:
        keys_found.append(suffix_key)

    if not keys_found:
        print(f"Suffix '{word}' not found in the tree.")
        return

    # Combine occurrences for each matching leaf key.
    combined_occurrences = {}
    for key in keys_found:
        leaf_id = suffix_to_id[key]
        data = load_occurrences(cursor, leaf_id)
        for book_id, offsets in data.items():
            combined_occurrences.setdefault(book_id, []).extend(offsets)

    # Sort the offsets for each book.
    for book_id in combined_occurrences:
        combined_occurrences[book_id].sort()

    # Print the combined search results (displaying the numeric book IDs).
    print(f"Combined search results for '{word}':")
    for book_id, offsets in combined_occurrences.items():
        offsets_str = ", ".join(map(str, offsets))
        print(f"Book ID {book_id}: Offsets: ({offsets_str}), Occurrences: {len(offsets)}")

def main():
    # 1) Load or build the suffix tree.
    trie, suffix_to_id = load_tree()
    if trie is None:
        # a) Load vocabulary (Moby Words)
        words = load_moby_words()  # Replace with your vocabulary loader
        # b) Build the suffix tree and mapping.
        trie, suffix_to_id = build_suffix_tree(words)
        print(f"Built suffix tree with {len(suffix_to_id)} unique suffixes.")
        # c) Save the tree for future use.
        save_tree(trie, suffix_to_id)
        # # d) Set up the JSON-based database.
        # conn, cursor = setup_database("leaves.db")
        # # e) Index the books from the folder (using numeric book IDs).
        # folder = "Gutenberg_Top_100"  # Ensure this folder exists and contains .txt files.
        # occurrences_map = index_books(folder, suffix_to_id, cursor)
        # # f) Bulk insert occurrences into the mapping table.
        # store_occurrences(cursor, occurrences_map)
        # conn.commit()

    db_name = "leaves.db"
    # Check if the database already exists and if not creating the db.
    if not os.path.exists(db_name):
        # d) Set up the JSON-based database.
        conn, cursor = setup_database("leaves.db")
        # e) Index the books from the folder (using numeric book IDs).
        folder = "Gutenberg_Top_100"  # Ensure this folder exists and contains .txt files.
        occurrences_map = index_books(folder, suffix_to_id, cursor)
        print(f"Indexed {len(occurrences_map)} unique suffix occurrences.\n Inserting into the database...")
        # f) Bulk insert occurrences into the mapping table.
        store_occurrences(cursor, occurrences_map)
        conn.commit()


    # 2) Search loop: prompt the user for a suffix to search.
    while True:
        query = input("Enter a suffix to search (or type 'exit' to quit): ").strip()
        if query.lower() in ["exit", "q"]:
            break
        search_word(query, suffix_to_id, cursor)

    # 3) Close the database connection.
    conn.close()
    print("Done indexing and searching.")

if __name__ == "__main__":
    main()
