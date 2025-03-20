import os
import pickle
import datrie
import string
import nltk
from nltk.tokenize import word_tokenize

from moby_words import load_moby_words

nltk.download('punkt')  # Ensure NLTK's tokenization data is available

MOBY_TRIE_FILE = "moby_trie.pkl"
BOOK_TRIE_FILE = "book_trie.pkl"
BOOKS_DIR = "Gutenberg_Top_100"

###############################################################################
# Step 1 Helpers: Build/Load Moby Dictionary Trie
###############################################################################
def create_trie():
    import string
    return datrie.Trie(string.ascii_lowercase)

def save_trie(filename, trie):
    """Pickle a datrie.Trie by first converting it to a dictionary."""
    with open(filename, "wb") as f:
        pickle.dump(dict(trie.items()), f)

def load_trie(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                trie = create_trie()
                for key, value in data.items():
                    # Check if the value is in the right format ([freq, offsets]) or True (Moby)
                    # We'll accept either so we don't break old pickles.
                    # If it's not acceptable, rebuild.
                    if isinstance(value, list) and len(value) == 2:
                        trie[key] = value
                    elif value is True or value is False:
                        trie[key] = value
                    else:
                        raise ValueError("Incompatible trie data format.")
                return trie
        except (EOFError, pickle.UnpicklingError, ValueError):
            print(f"Corrupt or incompatible data in {filename}. Rebuilding.")
            os.remove(filename)
    return None

def build_moby_trie():
    trie = load_trie(MOBY_TRIE_FILE)
    if trie is not None:
        print("Moby trie already exists. Loaded from cache.")
        return trie

    print("STEP 1: Building the trie with Moby words...")
    moby_words = load_moby_words()

    trie = create_trie()
    for word in moby_words:
        w = word.strip().lower()
        if w:
            trie[w] = True  # Mark as valid English word

    save_trie(MOBY_TRIE_FILE, trie)
    print("Moby trie built and saved as", MOBY_TRIE_FILE)
    return trie

###############################################################################
# Step 2 Helpers: Parse Books & Build "book trie" with frequency & offsets
###############################################################################
def load_books(directory):
    """
    Reads all .txt files from 'directory' into a dict {filename: full_text}.
    """
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

def build_book_trie(moby_trie):
    book_trie = load_trie(BOOK_TRIE_FILE)
    if book_trie is not None:
        print("Book trie already exists. Loaded from cache.")
        return book_trie

    print("STEP 2: Parsing books in", BOOKS_DIR)
    books = load_books(BOOKS_DIR)

    book_trie = create_trie()

    combined_offset = 0
    for title, text in books.items():
        print(f"  Indexing '{title}' (length {len(text)} chars)")

        tokens = word_tokenize(text.lower())
        for token in tokens:
            cleaned = token.strip(string.punctuation)
            if not cleaned:
                # It's purely punctuation. Still advance offset by length of token + 1
                combined_offset += len(token) + 1
                continue

            # Only index words that are recognized in the Moby trie
            if cleaned in moby_trie:
                if cleaned not in book_trie:
                    # We'll store [frequency, [offsets]]
                    book_trie[cleaned] = [1, [combined_offset]]
                else:
                    book_trie[cleaned][0] += 1
                    book_trie[cleaned][1].append(combined_offset)

            # Advance offset by length of the original token plus 1 (for spacing)
            combined_offset += len(token) + 1

    # Save the resulting trie
    save_trie(BOOK_TRIE_FILE, book_trie)
    print("All books have been parsed. Book trie saved as", BOOK_TRIE_FILE)
    return book_trie

###############################################################################
# NEW OR MODIFIED: Helper to dynamically add a missing word
###############################################################################
def dynamic_add_missing_word(book_trie, query, books):
    """
    Scan all books for 'query' by tokenizing again and matching exactly.
    If found, add [frequency, offsets] to book_trie and save it.
    Return (frequency, offsets) or (None, None) if not found at all.
    """
    w = query.lower()
    freq = 0
    offsets = []
    combined_offset = 0

    for title, text in books.items():
        tokens = word_tokenize(text.lower())
        for token in tokens:
            cleaned = token.strip(string.punctuation)
            if not cleaned:
                # If it's purely punctuation, still increment offset
                combined_offset += len(token) + 1
                continue

            if cleaned == w:
                freq += 1
                offsets.append(combined_offset)

            combined_offset += len(token) + 1

    if freq > 0:
        book_trie[w] = [freq, offsets]
        # Persist changes so it's there next time
        save_trie(BOOK_TRIE_FILE, book_trie)
        return freq, offsets
    return None, None

###############################################################################
# Step 3: Search for a word in the "book trie" (modified to add missing words)
###############################################################################
def search_word(book_trie, query, books):
    w = query.lower()
    if w in book_trie:
        freq, offsets = book_trie[w]
        print(f"\n'{w}' FOUND in the trie!")
        print(f"  Frequency: {freq}")
        print(f"  Offsets (first 20): {offsets[:20]}")
    else:
        print(f"\n'{w}' NOT FOUND in the trie. Scanning books for it...")
        freq, offsets = dynamic_add_missing_word(book_trie, w, books)
        if freq:
            print(f"  -> Found '{w}' {freq} times across all books. Added to trie.")
            print(f"  -> Offsets (first 20): {offsets[:20]}")
        else:
            print(f"  -> '{w}' does not appear in the books at all.")

###############################################################################
# Main: Tie it all together in 3 steps
###############################################################################
def main():
    # Step 1: Build the Moby trie (or load if exists)
    moby_trie = build_moby_trie()

    # Step 2: Parse the books & build the book trie (or load if exists)
    book_trie = build_book_trie(moby_trie)

    # NEW: We'll load the full book texts so we can re-scan them if user queries a missing word.
    print("Loading full book texts into memory...")
    books = load_books(BOOKS_DIR)

    # Step 3: Prompt the user for search
    print("\nSTEP 3: Search for a word in the indexed books. (type 'exit' to quit)")
    while True:
        query = input("\nSearch> ").strip()
        if query.lower() == "exit":
            print("Exiting. Goodbye!")
            break
        search_word(book_trie, query, books)

if __name__ == "__main__":
    main()
