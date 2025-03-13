import os
import pickle
from pytrie import StringTrie

# Constants
BOOKS_DIR = "Gutenberg_Top_100"
TRIE_FILE = "trie_offsets.pkl"

def build_trie():
    """
    Reads all tokenized books, builds a trie with word occurrences (offsets), and saves it.
    """
    trie = StringTrie()
    
    for filename in os.listdir(BOOKS_DIR):
        file_path = os.path.join(BOOKS_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    words = f.read().split()  # Read words from cleaned text
                
                # Insert words into the trie, storing offsets
                for index, word in enumerate(words):
                    if word not in trie:
                        trie[word] = {"count": 0, "offsets": []}
                    
                    trie[word]["count"] += 1
                    trie[word]["offsets"].append((filename, index))  # Store filename and position

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
    Returns the word count and its offsets if found.
    """
    return trie.get(word, {"count": 0, "offsets": []})

def search_prefix(trie, prefix):
    """
    Returns a list of words that start with the given prefix.
    """
    return list(trie.keys(prefix))

def get_context(filename, index, search_word, window=5):
    """
    Retrieves context around a word in the given file and highlights the word.
    """
    file_path = os.path.join(BOOKS_DIR, filename)
    if not os.path.exists(file_path):
        return f"File {filename} not found."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = f.read().split()
        
        start = max(0, index - window)
        end = min(len(words), index + window + 1)
        context_words = words[start:end]

        # Highlight the searched word
        context_words[window] = f"**{context_words[window]}**"

        return " ".join(context_words)

    except Exception as e:
        return f"Error reading {filename}: {e}"

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
                    result = search_word(trie, word)

                    if result["count"] > 0:
                        print(f"'{word}' appears {result['count']} times.")

                        # Group by filename and sort by frequency
                        book_counts = {}
                        for filename, _ in result["offsets"]:
                            book_counts[filename] = book_counts.get(filename, 0) + 1
                        
                        sorted_books = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)

                        for filename, _ in sorted_books[:3]:  # Show results from top 3 books
                            occurrences = [offset for offset in result["offsets"] if offset[0] == filename][:3]
                            for _, index in occurrences:
                                context = get_context(filename, index, word)
                                print(f"- Found in {filename} at position {index}: ... {context} ...")
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
