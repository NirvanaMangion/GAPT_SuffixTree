import os
import re

def tokenize_text(text):
    """
    Tokenizes text into words by splitting on whitespace and removing non-alphabetic characters.
    """
    tokens = re.findall(r'\b[a-z]+\b', text.lower())  # Extract words only
    return tokens

def process_downloaded_books(directory):
    """
    Process all text files in the given directory, tokenize the text, and return tokens.
    """
    all_tokens = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                tokens = tokenize_text(text)
                all_tokens[filename] = tokens
                print(f"Processed and tokenized: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    return all_tokens

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    if os.path.exists(download_dir):
        tokens_dict = process_downloaded_books(download_dir)
        for book, tokens in tokens_dict.items():
            print(f"{book}: {tokens[:10]}...")  # Print first 10 tokens for preview
    else:
        print(f"Directory '{download_dir}' does not exist.")
