import os
import re
import nltk
nltk.data.path.append('nltk_data')
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

def tokenize_text(cleaned_text):
    """
    Tokenizes cleaned text into words using NLTK's word_tokenize function.
    """
    tokens = word_tokenize(cleaned_text)  # Tokenize without redundant lowercase conversion
    tokens = [word for word in tokens if word.isalpha()]  # Keep only alphabetic words
    return tokens

def process_downloaded_books(directory):
    """
    Process all text files in the given directory, clean and tokenize the text, and overwrite the files.
    """
    all_tokens = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                
                cleaned_text = clean_text(text)
                tokens = tokenize_text(cleaned_text)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(" ".join(tokens))
                
                all_tokens[filename] = tokens
                print(f"Processed and cleaned & tokenized: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    return all_tokens

if __name__ == "__main__":
    download_dir = "Gutenberg_Books"
    if os.path.exists(download_dir):
        tokens_dict = process_downloaded_books(download_dir)
        for book, tokens in tokens_dict.items():
            print(f"{book}: {tokens[:10]}...")  # Print first 10 tokens for preview
    else:
        print(f"Directory '{download_dir}' does not exist.")