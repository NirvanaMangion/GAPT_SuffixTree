import os
import pickle
import datrie
import string
import nltk
from nltk.tokenize import word_tokenize

PICKLE_FILE = "book_trie.pkl"

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

def process_books(books):
    """
    Indexes words in the provided books using the Trie.
    
    Args:
        books (dict): Dictionary where keys are book titles and values are book contents as strings.
    """
    trie = load_trie(PICKLE_FILE)
    if trie is not None:
        print("Trie loaded from cache.")
        return trie

    trie = create_trie()
    
    print("Processing books and indexing words...")

    position = 0
    for book_title, text in books.items():
        print(f"Indexing: {book_title}")

        text = text.lower()
        words = word_tokenize(text)

        for word in words:
            if word.isalpha():  # Store only alphabetic words
                if word in trie:
                    trie[word].append(position)
                else:
                    trie[word] = [position]
            position += len(word) + 1  # Track offset in book

    save_trie(PICKLE_FILE, trie)
    print("Trie built and saved.")
    return trie

def search_word(trie, word):
    """Searches for a word in the Trie and returns offsets with frequency."""
    word = word.lower()
    if word in trie:
        offsets = trie[word]  # Already stored as a list
        frequency = len(offsets)

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
    # Example: Pass a dictionary of books directly
    books = {
        "Pride and Prejudice": open("book_downloads/book1.txt", encoding="utf-8").read(),
        "Alice in Wonderland": open("book_downloads/book2.txt", encoding="utf-8").read()
    }

    trie = process_books(books)

    while True:
        query = input("\nEnter a word to search (or type 'exit' to quit): ").strip().lower()
        if query == "exit":
            break
        search_word(trie, query)
