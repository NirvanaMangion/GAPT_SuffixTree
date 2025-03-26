import os
import re
from collections import defaultdict

from suffix_tree import build_suffix_tree, save_tree, load_tree
from db_tree import setup_database, store_occurrences, load_occurrences
from moby_words import load_moby_words

def index_books(folder, suffix_to_id):
    """
    For each .txt file in 'folder', tokenize the text and record offsets for each entry.
    For a token like "hello" at token index x, record:
      - Full word: "#hello$" at offset x
      - Proper suffixes: "ello$" at offset x+1, "llo$" at offset x+2, ..., "$" at offset x+len(token)
    Returns a mapping:
      { leaf_id: { "doc_name": [offset1, offset2, ...], ... }, ... }
    """
    occurrences_map = defaultdict(lambda: defaultdict(list))

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            doc_name = filename  # Use filename as document ID
            print(f"Indexing {doc_name} ...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"Failed to read {doc_name}: {e}")
                continue

            # Tokenize text (extract all word characters, converted to lowercase)
            tokens = re.findall(r"\w+", text.lower())
            for token_index, token in enumerate(tokens):
                # Record full word entry with '#' in front.
                full_word = '#' + token + '$'
                leaf_id = suffix_to_id.get(full_word)
                if leaf_id is not None:
                    occurrences_map[leaf_id][doc_name].append(token_index)
                # Record proper suffixes (without the '#' prefix)
                for i in range(1, len(token) + 1):
                    suffix = token[i:] + '$'
                    leaf_id = suffix_to_id.get(suffix)
                    if leaf_id is not None:
                        occurrences_map[leaf_id][doc_name].append(token_index + i)
    return occurrences_map

def search_word(word, suffix_to_id, cursor):
    """
    Search for a suffix in the in-memory mapping.

    If a user types a plain word (e.g. "at"), it might be stored both as a full word ("#at$")
    and as a proper suffix ("at$"). This function retrieves both sets of occurrences and combines them.
    """
    from collections import defaultdict

    word = word.strip().lower()
    full_key = '#' + word + '$'
    suffix_key = word + '$'

    # Check if the keys exist in the suffix tree mapping
    keys_found = []
    if full_key in suffix_to_id:
        keys_found.append(full_key)
    if suffix_key in suffix_to_id:
        keys_found.append(suffix_key)

    if not keys_found:
        print(f"Suffix '{word}' not found in the tree.")
        return

    # Combine occurrences from all found keys.
    combined_occurrences = defaultdict(list)
    for key in keys_found:
        leaf_id = suffix_to_id[key]
        doc_occurrences = load_occurrences(cursor, leaf_id)
        for doc, offsets in doc_occurrences.items():
            combined_occurrences[doc].extend(offsets)

    # Optionally, sort offsets for clarity.
    for doc in combined_occurrences:
        combined_occurrences[doc].sort()

    # Print combined occurrences
    print(f"Combined search results for '{word}':")
    for doc, offsets in combined_occurrences.items():
        offsets_str = ", ".join(str(o) for o in offsets)
        total_count = len(offsets)
        print(f"  {doc}: off({offsets_str}), occurrences: {total_count}")

def main():
    trie, suffix_to_id = load_tree()

    if trie is None:
        # 1) Load vocabulary (Moby Words)
        words = load_moby_words()

        # 2) Build the suffix tree and create a mapping (suffix_to_id)
        trie, suffix_to_id = build_suffix_tree(words)
        print(f"Built suffix tree with {len(suffix_to_id)} unique suffixes.")

        #  3) Save the trie and mapping to a file
        save_tree(trie, suffix_to_id)

        # 4) Set up the single-table SQLite database
        conn, cursor = setup_database("leaves.db")

        # 5) Index the downloaded books (folder: "Gutenberg_Top_100")
        folder = "Gutenberg_Top_100"
        occurrences_map = index_books(folder, suffix_to_id)

        # 6) Save the occurrences (doc->offset mappings) in the 'leaves' table
        store_occurrences(cursor, occurrences_map)
        conn.commit()
    else:
        conn, cursor = setup_database("leaves.db")

    # 7) Search loop: repeatedly prompt the user for a suffix to search
    while True:
        query = input("Enter a suffix to search (or type 'exit' to quit): ").strip()
        if query.lower() in ["exit", "q"]:
            break
        search_word(query, suffix_to_id, cursor)

    conn.close()
    print("Done indexing and searching.")

if __name__ == "__main__":
    main()
