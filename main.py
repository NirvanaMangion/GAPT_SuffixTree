# main.py
import os
import re
from collections import defaultdict

from suffix_tree import build_suffix_tree,save_tree,load_tree
from db_tree import setup_database, store_occurrences, load_occurrences
from moby_words import load_moby_words

def index_books(folder, suffix_to_id):
    """
    For each .txt file in 'folder', tokenize the text and record offsets for each suffix.
    For a token like "hello" appearing at token index x, it records:
      "hello" at offset x,
      "ello" at offset x+1,
      "llo" at offset x+2, etc.
    Returns a mapping:
      { leaf_id: { "doc_name": [offset1, offset2, ...], ... }, ... }
    """
    occurrences_map = defaultdict(lambda: defaultdict(list))

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder, filename)
            doc_name = filename  # Using filename as document ID
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
                # For each possible suffix of the token:
                for char_offset in range(len(token)):
                    suffix = token[char_offset:]
                    leaf_id = suffix_to_id.get(suffix)
                    if leaf_id is not None:
                        # Record the occurrence with an adjusted offset:
                        # if the full token ("hello") is at token_index x,
                        # then the suffix "ello" (starting at position 1) is recorded at x+1, etc.
                        occurrence_position = token_index + char_offset
                        occurrences_map[leaf_id][doc_name].append(occurrence_position)
    return occurrences_map
def search_word(word, suffix_to_id, cursor):
    """
    Search for a suffix in the in-memory mapping. If found, retrieve the JSON occurrence data
    from the 'leaves' table and print all offsets and the total count.

    Format:
      Database for id <leaf_id>:
        <doc> of(<all offsets>), occurrences: <total_count>
    """
    word = word.strip().lower()
    if word not in suffix_to_id:
        print(f"Suffix '{word}' not found in the tree.")
        return

    leaf_id = suffix_to_id[word]
    doc_occurrences = load_occurrences(cursor, leaf_id)
    if not doc_occurrences:
        print(f"No occurrences found for suffix '{word}' (leaf_id={leaf_id}).")
        return

    print(f"Database for id {leaf_id}:")
    for doc, offsets in doc_occurrences.items():
        # Join all offsets into a string
        offsets_str = ", ".join(str(o) for o in offsets)
        total_count = len(offsets)
        print(f"  {doc} off({offsets_str}), occurrences: {total_count}")

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
        # Set up the connection and cursor
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
