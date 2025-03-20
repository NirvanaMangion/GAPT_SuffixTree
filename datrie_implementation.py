import os
import pickle
import datrie
import string
import nltk
from nltk.tokenize import word_tokenize
from moby_words import load_moby_words  # Import the Moby word list loader

PICKLE_FILE = "book_trie.pkl"
BOOKS_DIR = "Gutenberg_Top_100"  # Directory containing downloaded books

nltk.download('punkt')

def create_trie():
    """Creates a Trie that supports lowercase English words."""
    return datrie.Trie(string.ascii_lowercase)

def save_trie(filename, trie):
    """Pickles the trie to a file for persistence."""
    with open(filename, "wb") as f:
        pickle.dump(dict(trie.items()), f)  # Convert Trie to dictionary before pickling

def load_trie(filename):
    """Loads a pickled trie from a file if it exists."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                trie = create_trie()
                for key, value in data.items():
                    trie[key] = value  # Restore values properly
                return trie
        except (EOFError, pickle.UnpicklingError):
            print(f"Corrupt pickle file detected: {filename}. Rebuilding data.")
            os.remove(filename)
    return None

def load_books(directory):
    """Loads all books from the specified directory."""
    books = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
                books[filename] = f.read()
    return books

def process_books():
    """
    Indexes words in all books from the Gutenberg_Top_100 folder.
    """
    trie = load_trie(PICKLE_FILE)
    if trie is not None:
        print("Trie loaded from cache.")
        return trie

    trie = create_trie()
    books = load_books(BOOKS_DIR)
    moby_words = set(load_moby_words())  # Load Moby words for validation

    print("Processing books and indexing words...")

    for book_title, text in books.items():
        print(f"Indexing: {book_title}")

        text = text.lower()
        words = word_tokenize(text)

        position = 0  # Track position of each word
        for word in words:
            word = word.strip(string.punctuation)
            if word in moby_words:  # Only index valid words
                if word in trie:
                    trie[word].append(position)  # Append the offset to the list
                else:
                    trie[word] = [position]  # Store first occurrence
            position += len(word) + 1  # Track offset in book

    save_trie(PICKLE_FILE, trie)
    print("Trie built and saved.")
    return trie

def search_word(trie, word):
    """Searches for a word in the Trie and returns its frequency and offsets."""
    word = word.lower()
    if word in trie:
        offsets = trie[word]  # Retrieve list of positions
        frequency = len(offsets)  # Count occurrences

        print("\n" + "="*40)
        print(f"WORD FOUND: '{word}'")
        print(f"Frequency: {frequency} occurrence(s)")
        print(f"Offsets: {', '.join(map(str, offsets))}")
        print("="*40 + "\n")
        return {
            "word": word,
            "found": True,
            "frequency": frequency,
            "offsets": offsets
        }
    
    print("\n" + "="*40)
    print(f"WORD NOT FOUND: '{word}'")
    print("="*40 + "\n")
    return {
        "word": word,
        "found": False,
        "frequency": 0,
        "offsets": []
    }

if __name__ == "__main__":
    trie = process_books()

    while True:
        query = input("\nEnter a word to search (or type 'exit' to quit): ").strip().lower()
        if query == "exit":
            break
        search_word(trie, query)
