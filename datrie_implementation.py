import os
import pickle
import datrie
import string
import nltk
import re
from nltk.tokenize import word_tokenize

from moby_words import load_moby_words

nltk.download('punkt')  # Ensure NLTK's tokenization data is available

TRIE_FILE = "unified_trie.pkl"
BOOKS_DIR = "Gutenberg_Top_100"

###############################################################################
# Helper Functions for Datrie-based Trie Persistence
###############################################################################
def create_trie():
    # datrie requires a range of acceptable characters; we use lowercase a-z.
    return datrie.Trie(string.ascii_lowercase)

def save_trie(filename, trie):
   
    with open(filename, "wb") as f:
        pickle.dump(dict(trie.items()), f)

def load_trie(filename):

    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                trie = create_trie()
                for key, value in data.items():
                    if isinstance(value, list) and len(value) == 2:
                        trie[key] = value
                    else:
                        raise ValueError("Incompatible trie data format.")
                return trie
        except (EOFError, pickle.UnpicklingError, ValueError) as e:
            print(f"Corrupt or incompatible data in {filename}: {e}. Rebuilding.")
            os.remove(filename)
    return None

###############################################################################
# Step 1: Build Unified Trie from Moby Words
###############################################################################
def build_unified_trie():
    trie = load_trie(TRIE_FILE)
    if trie is not None:
        print("Unified trie loaded from cache.")
        return trie

    print("Building unified trie from Moby words with initial [0, []] values...")
    moby_words = load_moby_words()
    trie = create_trie()
    for word in moby_words:
        w = word.strip().lower()
        if w:
            # Initialize with frequency 0 and an empty list of occurrences.
            trie[w] = [0, []]
    save_trie(TRIE_FILE, trie)
    print("Unified trie built and saved as", TRIE_FILE)
    return trie

###############################################################################
# Step 2: Data Collection & Book Indexing
###############################################################################
def load_books(directory):
   
    books = {}
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return books

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            path = os.path.join(directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    books[filename] = f.read()
            except UnicodeDecodeError:
                print(f"Skipping unreadable file: {filename}")
    return books

def index_books(trie):
   
    print("Indexing books from", BOOKS_DIR)
    books = load_books(BOOKS_DIR)
    for doc, text in books.items():
        print(f"  Processing '{doc}' (length {len(text)} chars)")
        tokens = word_tokenize(text.lower())
        offset = 0  # Track character offset within the current document.
        for token in tokens:
            cleaned = token.strip(string.punctuation)
            if not cleaned:
                # Advance offset for punctuation-only tokens.
                offset += len(token) + 1
                continue

            # Only update words that are in our Moby-based unified trie.
            if cleaned in trie:
                freq, occurrences = trie[cleaned]
                freq += 1
                # Store the document name and offset where the word occurred.
                occurrences.append((doc, offset))
                trie[cleaned] = [freq, occurrences]
            offset += len(token) + 1

    save_trie(TRIE_FILE, trie)
    print("Books indexed. Unified trie updated and saved as", TRIE_FILE)
    return trie, books

###############################################################################
# Step 3: Search Functionality: Exact and Regex-based Pattern Matching
###############################################################################
def search_word(trie, query):
  
    w = query.lower()
    if w in trie:
        freq, occurrences = trie[w]
        print(f"\n'{w}' FOUND in the trie!")
        print(f"  Frequency: {freq}")
        print(f"  Occurrences (first 20): {occurrences[:20]}")
    else:
        print(f"\n'{w}' is not in the dictionary and therefore not indexed.")

def regex_search(trie, pattern):
   
    print(f"\nSearching for pattern: {pattern}")
    try:
        regex = re.compile(pattern)
    except re.error as e:
        print(f"Invalid regex: {e}")
        return

    matches = {}
    # Iterate over all words in the trie (the dictionary size should be reasonable)
    for word in trie.keys():
        if regex.search(word):
            matches[word] = trie[word]

    if matches:
        print("Pattern matches found:")
        for word, (freq, occurrences) in matches.items():
            print(f"Word: '{word}', Frequency: {freq}, Occurrences (first 5): {occurrences[:5]}")
    else:
        print("No words matching the pattern were found.")

###############################################################################
# Main: Tie Everything Together
###############################################################################
def main():
    # Step 1: Build the unified trie from the Moby dictionary.
    trie = build_unified_trie()

    # Step 2: Index the books into the unified trie.
    trie, books = index_books(trie)

    # Interactive search: exact search or regex-based search.
    print("\nInteractive search mode. Type 'exit' to quit.")
    print("To perform a regex search, prefix your query with 'regex:'.")
    while True:
        query = input("\nSearch> ").strip()
        if query.lower() == "exit":
            print("Exiting. Goodbye!")
            break
        elif query.startswith("regex:"):
            pattern = query[len("regex:"):].strip()
            regex_search(trie, pattern)
        else:
            search_word(trie, query)

if __name__ == "__main__":
    main()
