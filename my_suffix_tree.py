import os
import pickle
from suffix_trees.STree import STree
from cleaned_tokenized import process_books

PICKLE_FILE = "tokenized_data.pkl"
TREE_CACHE_FILE = "suffix_trees.pkl"

def save_data(filename, data):
    """Generic function to save data using pickle."""
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_data(filename):
    """Generic function to load data using pickle."""
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            print(f"Corrupt pickle file detected: {filename}. Rebuilding data.")
            os.remove(filename)
    return None

def get_tokenized_books(directory):
    """Retrieves tokenized books, using cached data if available."""
    tokenized_books = load_data(PICKLE_FILE)
    if tokenized_books is None:
        tokenized_books = process_books(directory)
        save_data(PICKLE_FILE, tokenized_books)
    return tokenized_books

def build_suffix_trees(tokenized_books):
    """Builds and caches suffix trees for all books."""
    suffix_trees = load_data(TREE_CACHE_FILE)
    if suffix_trees is None:
        suffix_trees = {book: STree(data["text"]) for book, data in tokenized_books.items()}
        save_data(TREE_CACHE_FILE, suffix_trees)
    return suffix_trees

def search_in_books(suffix_trees, tokenized_books, query):
    """Searches for a word in prebuilt suffix trees."""
    results = {}
    
    for book, tree in suffix_trees.items():
        text = tokenized_books[book]["text"]
        matches = tree.find_all(query)

        if matches:
            word_matches = [text[:match].count(" ") for match in matches]
            results[book] = word_matches
    
    if results:
        print(f"'{query}' found in:")
        sorted_results = sorted(results.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (book, offsets) in enumerate(sorted_results, 1):
            print(f"{i}. {book} ({len(offsets)} occurrences)")
        
        choice = input("Select a book number to see word offsets (or 'exit' to cancel): ")
        if choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(sorted_results):
                selected_book, offsets = sorted_results[choice]
                print(f"Word Offsets for '{query}' in {selected_book}: {sorted(offsets)}")
    else:
        print(f"'{query}' not found in any book.")

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    
    if os.path.exists(download_dir):
        tokenized_books = get_tokenized_books(download_dir)
        suffix_trees = build_suffix_trees(tokenized_books)
        
        while True:
            query = input("Enter a word to search (or type 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            search_in_books(suffix_trees, tokenized_books, query)
    else:
        print(f"Directory '{download_dir}' does not exist.")
