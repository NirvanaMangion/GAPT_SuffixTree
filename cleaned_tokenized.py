import os
import re
import nltk
from nltk.tokenize import word_tokenize

# Download required NLTK resources
nltk.download('punkt')

def clean_text(text):
    """
    Cleans the input text:
    - Converts to lowercase
    - Removes numbers and special symbols (except spaces)
    - Ensures only one space between words
    """
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)  # Remove non-alphabetic characters
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space
    return text

def extract_text_from_rtf(rtf_content):
    """
    Extracts plain text from RTF content by removing RTF formatting.
    """
    text = re.sub(r'\{\\.*?\}', '', rtf_content)  # Remove RTF metadata
    text = re.sub(r'\\[a-zA-Z0-9]+', '', text)  # Remove RTF commands
    text = text.replace('\n', ' ').replace('\r', ' ')  # Normalize whitespace
    return text.strip()

def process_and_save_book(file_path):
    """
    Reads, extracts text from RTF, cleans, tokenizes, and overwrites the book file with cleaned text.
    Returns dictionary.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            rtf_content = f.read()

        extracted_text = extract_text_from_rtf(rtf_content)
        cleaned_text = clean_text(extracted_text)

        # Save the cleaned text back to the same file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Cleaned: {file_path}")

        # Tokenizing after saving
        words = cleaned_text.split()
        tokens_with_offsets = [(word, idx) for idx, word in enumerate(words)]

        return {"text": cleaned_text, "offsets": tokens_with_offsets}
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def process_books(directory):
    """
    Processes all books in a directory.
    Overwrites files with cleaned text.
    Returns dictionary.
    """
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return {}

    tokenized_books = {}
    for filename in sorted(os.listdir(directory)):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".rtf"):
            book_data = process_and_save_book(file_path)
            if book_data:
                tokenized_books[filename] = book_data

    return tokenized_books

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    books = process_books(download_dir)
    