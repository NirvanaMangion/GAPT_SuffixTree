import os
import re
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK tokenizer data
nltk.download('punkt')

def clean_text(text):
    """
    Convert text to lowercase and replace numbers & special symbols with spaces.
    """
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)  # Keep only letters and spaces
    return text

def tokenize_text_with_offsets(cleaned_text, original_text):
    """
    Tokenizes cleaned text into words while recording character offsets from the original text.
    """
    tokens_with_offsets = []
    for match in re.finditer(r'\b[a-z]+\b', original_text, re.IGNORECASE):
        token = match.group()
        offset = match.start()
        tokens_with_offsets.append((token, offset))
    return tokens_with_offsets

def process_downloaded_books(directory):
    """
    Process all text files in the given directory, clean and tokenize the text,
    recording offsets for each token.
    """
    all_tokens = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    original_text = f.read()
                
                cleaned_text = clean_text(original_text)
                tokens_with_offsets = tokenize_text_with_offsets(cleaned_text, original_text)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(" ".join([token for token, _ in tokens_with_offsets]))
                
                all_tokens[filename] = tokens_with_offsets
                print(f"Processed and cleaned & tokenized: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    return all_tokens

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    if os.path.exists(download_dir):
        tokens_dict = process_downloaded_books(download_dir)
        for book, tokens in tokens_dict.items():
            print(f"{book}: {tokens[:10]}...")  # Print first 10 tokens with offsets for preview
    else:
        print(f"Directory '{download_dir}' does not exist.")