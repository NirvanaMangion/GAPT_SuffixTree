import os
import re
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK tokenizer data
nltk.download('punkt')

def clean_text(text):
    """Convert text to lowercase and remove numbers & special characters except spaces."""
    return re.sub(r'[^a-z\s]', ' ', text.lower())

def tokenize_text_with_offsets(text):
    """Tokenizes text and records offsets starting from 0."""
    tokens_with_offsets = []
    words = text.split()
    offset = 0
    for word in words:
        tokens_with_offsets.append((word, offset))
        offset += 1  # Increment offset based on token index
    return tokens_with_offsets

def process_downloaded_books(directory):
    """
    Reads all text files in the directory, cleans, tokenizes, and records offsets for each token.
    Returns a dictionary {filename: [(token, offset), ...]}
    """
    all_tokens = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    original_text = f.read()

                tokens_with_offsets = tokenize_text_with_offsets(original_text)
                all_tokens[filename] = tokens_with_offsets
                print(f"Processed: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return all_tokens

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    if os.path.exists(download_dir):
        tokens_dict = process_downloaded_books(download_dir)
        for book, tokens in tokens_dict.items():
            print(f"{book}: {tokens[:10]}...")  # Preview first 10 tokens with offsets
    else:
        print(f"Directory '{download_dir}' does not exist.")
