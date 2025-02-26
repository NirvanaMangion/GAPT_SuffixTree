import os
import re
import nltk
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
nltk.download('punkt')

def clean_text(text):
    
    # Clean and tokenize text:

    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z\s]', ' ', text)  # Keep only letters and spaces
    tokens = word_tokenize(text)  # Tokenize text
    return ' '.join(tokens)  # Reconstruct cleaned text

def process_downloaded_books(directory):
    """
    Process all text files in the given directory, clean the text, and overwrite the files.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                cleaned_text = clean_text(text)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)
                print(f"✅ Processed and cleaned: {filename}")  # Confirmation message
            except Exception as e:
                print(f"❌ Error processing file {filename}: {e}")

if __name__ == "__main__":
    download_dir = "Gutenberg_Top_100"
    if os.path.exists(download_dir):
        print("📂 Processing downloaded books...")
        process_downloaded_books(download_dir)
        print("🎉 All books have been cleaned and tokenized!")
    else:
        print(f"⚠️ Directory '{download_dir}' does not exist.")
        