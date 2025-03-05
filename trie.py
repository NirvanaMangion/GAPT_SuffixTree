import os
import pickle
from pytrie import StringTrie

# Constants
BOOKS_DIR = "Gutenberg_Top_100"
TRIE_FILE = "trie.pkl"

def build_trie():
    """
    Reads all tokenized books, builds a trie with word frequency, and saves it.
    """
    trie = StringTrie()
    
    for filename in os.listdir(BOOKS_DIR):
        file_path = os.path.join(BOOKS_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    words = f.read().split()  # Read words from cleaned text

                # Insert words into trie, storing their frequency
                for word in words:
                    trie[word] = trie.get(word, 0) + 1
                
                print(f"Processed {filename}.")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Save the trie to a file
    with open(TRIE_FILE, "wb") as f:
        pickle.dump(trie, f)

    print(f"Trie built and saved with {len(trie)} words.")

def load_trie():
    """
    Loads the saved trie from a file.
    """
    try:
        with open(TRIE_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Trie file not found. Run the script to build the trie first.")
        return None

def search_word(trie, word):
    """
    Searches for a specific word in the trie.
    Returns the word count if found, otherwise 0.
    """
    return trie.get(word, 0)

def search_prefix(trie, prefix):
    """
    Returns a list of words that start with the given prefix.
    """
    return list(trie.keys(prefix))

if __name__ == "__main__":
    print("1. Build and save the trie")
    print("2. Load and search the trie")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        build_trie()

    elif choice == "2":
        trie = load_trie()
        if trie:
            while True:
                print("\nOptions:")
                print("1. Search for a word")
                print("2. Find words with a prefix")
                print("3. Exit")

                choice = input("Enter your choice: ").strip()

                if choice == "1":
                    word = input("Enter a word to search: ").strip().lower()
                    count = search_word(trie, word)
                    if count:
                        print(f"'{word}' appears {count} times.")
                    else:
                        print(f"'{word}' not found.")

                elif choice == "2":
                    prefix = input("Enter a prefix: ").strip().lower()
                    matches = search_prefix(trie, prefix)
                    print(f"Words starting with '{prefix}': {matches[:10]}")  # Show first 10 matches

                elif choice == "3":
                    print("Exiting...")
                    break

                else:
                    print("Invalid choice, try again.")
    else:
        print("Invalid selection. Exiting...")
