import os
from cleaned_tokenized import clean_text, tokenize_text_with_offsets  # Import from cleaned_tokenized.py

class SuffixTreeNode:
    def __init__(self):
        self.children = {}
        self.indexes = []  # Store (book, offset) pairs

class SuffixTree:
    def __init__(self):
        self.root = SuffixTreeNode()
    
    def add_token(self, token, book_name, offset):
        node = self.root
        for char in token:
            if char not in node.children:
                node.children[char] = SuffixTreeNode()
            node = node.children[char]
        node.indexes.append((book_name, offset))
    
    def search(self, pattern):
        node = self.root
        for char in pattern:
            if char in node.children:
                node = node.children[char]
            else:
                return []  # Pattern not found
        return node.indexes  # Return list of (book, offset) tuples

def process_books(directory, suffix_tree):
    """Process books and add tokens to the suffix tree with offsets starting from 0."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                
                cleaned_text = clean_text(text)  # Using clean_text from cleaned_tokenized.py
                tokens_with_offsets = tokenize_text_with_offsets(cleaned_text)  # Using tokenize_text_with_offsets from cleaned_tokenized.py
                
                for token, offset in tokens_with_offsets:
                    suffix_tree.add_token(token, filename, offset)
                
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    suffix_tree = SuffixTree()
    
    if os.path.exists(download_dir):
        process_books(download_dir, suffix_tree)
        print("Suffix tree built successfully!")
        
        while True:
            query = input("Enter a word to search (or type 'exit' to quit): ")
            if query.lower() == 'exit':
                break
            results = suffix_tree.search(query)
            if results:
                print(f"'{query}' found in:")
                for book, offset in results:
                    print(f" - {book} at token index {offset}")
            else:
                print(f"'{query}' not found in any book.")
    else:
        print(f"Directory '{download_dir}' does not exist.")
