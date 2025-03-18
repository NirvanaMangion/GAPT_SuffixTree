import os
import datrie
import string

def create_trie():
    """Creates a Trie with full Unicode range."""
    return datrie.Trie(ranges=[(0, 0x10FFFF)])

def process_book(file_path):
    """Reads a book, tokenizes words, and stores word offsets in a trie."""
    trie = create_trie()
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    words = content.split()
    offset = 0
    
    for word in words:
        word = word.strip(string.punctuation).lower()
        if word:
            if word in trie:
                trie[word].append(offset)
            else:
                trie[word] = [offset]
        offset += len(word) + 1  # Account for spaces
    
    return trie

def build_index(folder_path):
    """Processes all books in a folder and creates a trie for each."""
    book_tries = {}
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            print(f"Indexing: {file_name}")
            book_tries[file_name] = process_book(file_path)
    return book_tries

def search_word(book_tries, book_name, word):
    """Searches for a word in a specific book and returns offsets."""
    word = word.lower()
    if book_name in book_tries and word in book_tries[book_name]:
        return book_tries[book_name][word]
    return []

# Example Usage
folder = "Gutenberg_Top_100"
book_indices = build_index(folder)

# Search for a word in a specific book
offsets = search_word(book_indices, "some_book.txt", "example")
print("Word found at offsets:", offsets)