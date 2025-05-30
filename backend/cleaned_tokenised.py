import os
import re
import nltk

# Add custom NLTK data path
nltk.data.path.append('nltk_data')

# Download tokenizer model if not already present
nltk.download('punkt')

from nltk.tokenize import word_tokenize


# Clean text: lowercase + remove non-letters
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)  # keep letters and spaces only
    return text


# Tokenize cleaned text using NLTK
def tokenize_text(cleaned_text):
    tokens = word_tokenize(cleaned_text)  # split into tokens
    tokens = [word for word in tokens if word.isalpha()]  # keep alphabetic words
    return tokens


# Process all .txt files in a folder
def process_downloaded_books(directory):
    all_tokens = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                cleaned_text = clean_text(text)     # lowercase & clean
                tokens = tokenize_text(cleaned_text)  # tokenize

                # Overwrite file with cleaned tokens
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(" ".join(tokens))

                all_tokens[filename] = tokens
                print(f"Processed and cleaned & tokenized: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    return all_tokens


# Main execution
if __name__ == "__main__":
    download_dir = "Gutenberg_Books"
    if os.path.exists(download_dir):
        tokens_dict = process_downloaded_books(download_dir)
        for book, tokens in tokens_dict.items():
            print(f"{book}: {tokens[:10]}...")  # show preview tokens
    else:
        print(f"Directory '{download_dir}' does not exist.")
